# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Check Out — Guest Check-Out Process Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


class VLCheckOut(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLCO-.YYYY.-.#####", doc=self)

	def validate(self):
		self.validate_reservation()
		self.validate_folio_balance()
		self.set_defaults()

	def on_submit(self):
		self.update_reservation_status()
		self.update_room_status()
		self.close_folio()
		self.update_guest_stats()
		self.post_late_checkout_charge()
		frappe.publish_realtime("vl_check_out", {
			"guest": self.guest_name, "room": self.room
		})

	def on_cancel(self):
		frappe.db.set_value("VL Reservation", self.reservation, "status", "Checked In",
			update_modified=False)
		frappe.db.set_value("VL Room", self.room, {
			"room_status": "Occupied", "fo_status": "Occupied",
		})

	def validate_reservation(self):
		if not self.reservation:
			frappe.throw(_("Reservation is required"))
		res = frappe.get_doc("VL Reservation", self.reservation)
		if res.status != "Checked In":
			frappe.throw(_("Reservation {0} is not checked in (Status: {1})").format(
				self.reservation, res.status))
		self.guest = res.guest
		self.guest_name = res.guest_name
		self.room = res.room
		self.folio = res.folio

	def validate_folio_balance(self):
		if self.folio:
			balance = flt(frappe.db.get_value("VL Folio", self.folio, "balance"))
			self.folio_balance = balance
			if balance > 0 and not self.flags.force_checkout:
				frappe.msgprint(
					_("Folio {0} has outstanding balance of {1}").format(self.folio, balance),
					indicator="orange", alert=True
				)

	def set_defaults(self):
		if not self.check_out_time:
			self.check_out_time = now_datetime()

	def update_reservation_status(self):
		frappe.db.set_value("VL Reservation", self.reservation, "status", "Checked Out",
			update_modified=False)

	def update_room_status(self):
		frappe.db.set_value("VL Room", self.room, {
			"room_status": "Dirty", "fo_status": "Vacant",
			"housekeeping_status": "Dirty",
			"current_guest": None, "current_reservation": None, "current_folio": None,
		})
		# Auto-create housekeeping task
		self.create_hk_task()

	def close_folio(self):
		if self.folio and frappe.db.exists("VL Folio", self.folio):
			folio = frappe.get_doc("VL Folio", self.folio)
			if folio.docstatus == 0:
				folio.status = "Closed"
				folio.save(ignore_permissions=True)

	def update_guest_stats(self):
		if self.guest and frappe.db.exists("VL Guest", self.guest):
			guest = frappe.get_doc("VL Guest", self.guest)
			guest.total_stays = (guest.total_stays or 0) + 1
			guest.last_visit = now_datetime().date()
			guest.save(ignore_permissions=True)

	def post_late_checkout_charge(self):
		if self.is_late_checkout and flt(self.late_charge) > 0 and self.folio:
			from velara.utils import post_charge_to_folio
			post_charge_to_folio(
				self.folio, "Late Checkout", self.late_charge,
				_("Late checkout charge"), "VL Check Out", self.name
			)

	def create_hk_task(self):
		if frappe.db.exists("DocType", "VL HK Task"):
			task = frappe.new_doc("VL HK Task")
			task.room = self.room
			task.task_type = "Checkout Cleaning"
			task.scheduled_date = now_datetime().date()
			task.status = "Pending"
			task.priority = "High"
			task.insert(ignore_permissions=True)
