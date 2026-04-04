# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Spa Booking — Spa Appointment Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VLSpaBooking(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLSB-.YYYY.-.#####", doc=self)

	def validate(self):
		self.set_charge_amount()
		self.check_availability()

	def on_update(self):
		if self.status == "Completed" and not self.posted_to_folio and self.folio:
			self.post_to_folio()

	def set_charge_amount(self):
		if self.spa_service and not self.charge_amount:
			price = frappe.db.get_value("VL Spa Service", self.spa_service, "price")
			self.charge_amount = flt(price)

	def check_availability(self):
		if not self.booking_datetime or not self.therapist:
			return
		overlap = frappe.db.exists("VL Spa Booking", {
			"therapist": self.therapist, "booking_datetime": self.booking_datetime,
			"status": ["!=", "Cancelled"], "name": ["!=", self.name]
		})
		if overlap:
			frappe.throw(_("Therapist {0} already has a booking at this time").format(self.therapist))

	def post_to_folio(self):
		if self.folio and flt(self.charge_amount) > 0:
			from velara.utils import post_charge_to_folio
			post_charge_to_folio(
				self.folio, "Spa", self.charge_amount,
				_("Spa: {0}").format(self.spa_service),
				"VL Spa Booking", self.name
			)
			self.db_set("posted_to_folio", 1)
