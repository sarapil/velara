# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Check In — Guest Check-In Process Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, flt, getdate, today


class VLCheckIn(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLCI-.YYYY.-.#####", doc=self)

	def validate(self):
		self.validate_reservation()
		self.validate_room()
		self.set_defaults()

	def on_submit(self):
		self.update_reservation_status()
		self.update_room_status()
		self.create_folio_if_needed()
		frappe.publish_realtime("vl_check_in", {
			"guest": self.guest_name, "room": self.room
		})

	def on_cancel(self):
		self.revert_reservation_status()
		self.revert_room_status()

	def validate_reservation(self):
		if not self.reservation:
			frappe.throw(_("Reservation is required for check-in"))
		res = frappe.get_doc("VL Reservation", self.reservation)
		if res.docstatus != 1:
			frappe.throw(_("Reservation {0} is not submitted").format(self.reservation))
		if res.status in ("Cancelled", "No Show", "Checked In", "Checked Out"):
			frappe.throw(_("Reservation {0} cannot be checked in (Status: {1})").format(
				self.reservation, res.status))
		self.guest = res.guest
		self.guest_name = res.guest_name
		self.room = res.room

	def validate_room(self):
		if not self.room:
			frappe.throw(_("No room assigned to the reservation. Please assign a room first."))
		room = frappe.get_doc("VL Room", self.room)
		if room.room_status in ("Out of Order", "Out of Service"):
			frappe.throw(_("Room {0} is {1} and cannot be used for check-in").format(
				self.room, room.room_status))

	def set_defaults(self):
		if not self.check_in_time:
			self.check_in_time = now_datetime()

	def update_reservation_status(self):
		frappe.db.set_value("VL Reservation", self.reservation, "status", "Checked In",
			update_modified=False)

	def update_room_status(self):
		frappe.db.set_value("VL Room", self.room, {
			"room_status": "Occupied", "fo_status": "Occupied",
			"current_guest": self.guest, "current_reservation": self.reservation,
		})

	def revert_reservation_status(self):
		frappe.db.set_value("VL Reservation", self.reservation, "status", "Confirmed",
			update_modified=False)

	def revert_room_status(self):
		frappe.db.set_value("VL Room", self.room, {
			"room_status": "Available", "fo_status": "Vacant",
			"current_guest": None, "current_reservation": None,
		})

	def create_folio_if_needed(self):
		res = frappe.get_doc("VL Reservation", self.reservation)
		if not res.folio:
			folio = frappe.new_doc("VL Folio")
			folio.guest = self.guest
			folio.reservation = self.reservation
			folio.room = self.room
			folio.status = "Open"
			folio.folio_type = "Guest"
			folio.insert(ignore_permissions=True)
			frappe.db.set_value("VL Reservation", self.reservation, "folio", folio.name)
			frappe.db.set_value("VL Room", self.room, "current_folio", folio.name)
