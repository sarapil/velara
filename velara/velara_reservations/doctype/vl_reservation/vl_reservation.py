# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Reservation — Hotel Reservation Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, today, date_diff, now_datetime, add_days


class VLReservation(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLR-.YYYY.-.#####", doc=self)

	def validate(self):
		self.validate_dates()
		self.validate_room_type()
		self.validate_guest()
		self.calculate_nights()
		self.calculate_charges()
		self.validate_availability()

	def on_submit(self):
		if not self.status or self.status == "Draft":
			self.db_set("status", "Confirmed")
		if not self.confirmation_number:
			self.db_set("confirmation_number", self.name)
		self.update_room_status()

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		self.db_set("cancelled_on", now_datetime())
		self.release_room()

	def on_update_after_submit(self):
		self.update_room_status()

	def validate_dates(self):
		if not self.check_in_date or not self.check_out_date:
			frappe.throw(_("Check-in and Check-out dates are required"))
		if getdate(self.check_out_date) <= getdate(self.check_in_date):
			frappe.throw(_("Check-out date must be after Check-in date"))

	def validate_room_type(self):
		if not self.room_type:
			frappe.throw(_("Room Type is required"))

	def validate_guest(self):
		if not self.guest:
			frappe.throw(_("Guest is required"))
		self.guest_name = frappe.db.get_value("VL Guest", self.guest, "guest_name")

	def calculate_nights(self):
		if self.check_in_date and self.check_out_date:
			self.nights = date_diff(self.check_out_date, self.check_in_date)

	def calculate_charges(self):
		if not self.room_rate:
			if self.rate_plan:
				self.room_rate = flt(frappe.db.get_value("VL Rate Plan", self.rate_plan, "base_rate"))
			elif self.room_type:
				self.room_rate = flt(frappe.db.get_value("VL Room Type", self.room_type, "default_rate"))

		nights = cint(self.nights) or 1
		self.total_room_charges = flt(self.room_rate * nights, 2)
		discount = flt(self.discount_percent)
		self.net_total = flt(self.total_room_charges * (1 - discount / 100), 2) if discount else self.total_room_charges

	def validate_availability(self):
		if not self.room:
			return
		overlapping = frappe.db.sql("""
			SELECT name FROM `tabVL Reservation`
			WHERE room = %s AND name != %s AND docstatus = 1
				AND status NOT IN ('Cancelled', 'No Show', 'Checked Out')
				AND check_in_date < %s AND check_out_date > %s
		""", (self.room, self.name, self.check_out_date, self.check_in_date))
		if overlapping:
			frappe.throw(_("Room {0} is already reserved (Reservation: {1})").format(
				self.room, overlapping[0][0]))

	def update_room_status(self):
		if not self.room:
			return
		status_map = {"Confirmed": "Reserved", "Guaranteed": "Reserved", "Checked In": "Occupied"}
		fo_status = status_map.get(self.status)
		if fo_status:
			frappe.db.set_value("VL Room", self.room, {
				"fo_status": fo_status, "current_reservation": self.name, "current_guest": self.guest,
			})

	def release_room(self):
		if self.room:
			frappe.db.set_value("VL Room", self.room, {
				"fo_status": "Vacant", "current_reservation": None, "current_guest": None,
			})

	@frappe.whitelist()
	def assign_room(self, room):
		if not frappe.db.exists("VL Room", room):
			frappe.throw(_("Room {0} does not exist").format(room))
		self.room = room
		self.save(ignore_permissions=True)
		self.update_room_status()
		return room

	@frappe.whitelist()
	def create_folio(self):
		if self.folio:
			frappe.throw(_("Folio already exists: {0}").format(self.folio))
		folio = frappe.new_doc("VL Folio")
		folio.guest = self.guest
		folio.reservation = self.name
		folio.room = self.room
		folio.status = "Open"
		folio.folio_type = "Guest"
		folio.insert(ignore_permissions=True)
		self.db_set("folio", folio.name)
		return folio.name
