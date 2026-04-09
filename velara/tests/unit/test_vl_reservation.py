# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT

"""
Velara — Unit Tests for VL Reservation DocType
Tests validation, night calculation, charge computation, and availability logic.
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today, add_days, getdate


class TestVLReservation(IntegrationTestCase):
    """Tests for VL Reservation DocType controller."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ensure_room_type()
        cls._ensure_guest()

    @classmethod
    def _ensure_room_type(cls):
        if not frappe.db.exists("VL Room Type", "_Test Room Type"):
            frappe.get_doc({
                "doctype": "VL Room Type",
                "room_type_name": "_Test Room Type",
                "default_rate": 200,
            }).insert(ignore_permissions=True)

    @classmethod
    def _ensure_guest(cls):
        if not frappe.db.exists("VL Guest", {"guest_name": "_Test Guest"}):
            doc = frappe.get_doc({
                "doctype": "VL Guest",
                "guest_name": "_Test Guest",
                "first_name": "_Test",
                "last_name": "Guest",
            })
            doc.insert(ignore_permissions=True)
            cls.test_guest = doc.name
        else:
            cls.test_guest = frappe.db.get_value("VL Guest", {"guest_name": "_Test Guest"}, "name")

    def tearDown(self):
        for name in frappe.get_all("VL Reservation", filters={"guest_name": ["like", "_Test%"]}, pluck="name"):
            frappe.delete_doc("VL Reservation", name, force=True, ignore_permissions=True)
        frappe.db.rollback()

    def _make_reservation(self, **kwargs):
        """Helper to create a VL Reservation test record."""
        doc = frappe.get_doc({
            "doctype": "VL Reservation",
            "guest": kwargs.get("guest", self.test_guest),
            "room_type": kwargs.get("room_type", "_Test Room Type"),
            "check_in_date": kwargs.get("check_in_date", add_days(today(), 1)),
            "check_out_date": kwargs.get("check_out_date", add_days(today(), 4)),
            "room_rate": kwargs.get("room_rate", 200),
            "status": kwargs.get("status", "Draft"),
        })
        doc.insert(ignore_permissions=True)
        return doc

    # ── Date Validation ─────────────────────────────────────────

    def test_checkout_before_checkin_throws(self):
        """Check-out date before check-in should raise."""
        with self.assertRaises(frappe.exceptions.ValidationError):
            self._make_reservation(
                check_in_date=add_days(today(), 5),
                check_out_date=add_days(today(), 2),
            )

    def test_same_checkin_checkout_throws(self):
        """Check-out date equal to check-in should raise (zero nights)."""
        with self.assertRaises(frappe.exceptions.ValidationError):
            self._make_reservation(
                check_in_date=add_days(today(), 5),
                check_out_date=add_days(today(), 5),
            )

    # ── Night Calculation ───────────────────────────────────────

    def test_nights_calculated(self):
        """Nights should be calculated from check-in to check-out."""
        doc = self._make_reservation(
            check_in_date=add_days(today(), 1),
            check_out_date=add_days(today(), 4),
        )
        self.assertEqual(doc.nights, 3)

    def test_one_night_stay(self):
        """Single night stay should calculate as 1."""
        doc = self._make_reservation(
            check_in_date=add_days(today(), 1),
            check_out_date=add_days(today(), 2),
        )
        self.assertEqual(doc.nights, 1)

    # ── Charge Calculation ──────────────────────────────────────

    def test_total_charges_computed(self):
        """Total room charges = rate * nights."""
        doc = self._make_reservation(
            room_rate=200,
            check_in_date=add_days(today(), 1),
            check_out_date=add_days(today(), 4),
        )
        self.assertEqual(doc.total_room_charges, 600)  # 200 * 3 nights

    def test_discount_applied(self):
        """Net total should reflect discount percentage."""
        doc = frappe.get_doc({
            "doctype": "VL Reservation",
            "guest": self.test_guest,
            "room_type": "_Test Room Type",
            "check_in_date": add_days(today(), 1),
            "check_out_date": add_days(today(), 4),
            "room_rate": 200,
            "discount_percent": 10,
        })
        doc.insert(ignore_permissions=True)
        self.assertEqual(doc.nights, 3)
        self.assertEqual(doc.total_room_charges, 600)
        self.assertEqual(doc.net_total, 540)  # 600 * 0.9

    # ── CRUD ────────────────────────────────────────────────────

    def test_reservation_create_and_read(self):
        """Basic create and read cycle."""
        doc = self._make_reservation()
        self.assertTrue(frappe.db.exists("VL Reservation", doc.name))
        loaded = frappe.get_doc("VL Reservation", doc.name)
        self.assertEqual(loaded.guest, self.test_guest)

    # ── Guest Validation ────────────────────────────────────────

    def test_missing_guest_throws(self):
        """Creating reservation without guest should raise."""
        with self.assertRaises(frappe.exceptions.ValidationError):
            frappe.get_doc({
                "doctype": "VL Reservation",
                "room_type": "_Test Room Type",
                "check_in_date": add_days(today(), 1),
                "check_out_date": add_days(today(), 4),
                "room_rate": 200,
            }).insert(ignore_permissions=True)
