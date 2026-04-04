# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Event Booking — Event & Banquet Booking Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class VLEventBooking(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLEB-.YYYY.-.#####", doc=self)

	def validate(self):
		self.validate_dates()
		self.validate_venue_availability()
		self.calculate_balance()

	def validate_dates(self):
		if self.start_datetime and self.end_datetime:
			if self.end_datetime <= self.start_datetime:
				frappe.throw(_("End time must be after Start time"))

	def validate_venue_availability(self):
		if not self.venue or not self.start_datetime or not self.end_datetime:
			return
		overlap = frappe.db.sql("""
			SELECT name FROM `tabVL Event Booking`
			WHERE venue = %s AND name != %s
				AND status NOT IN ('Cancelled')
				AND start_datetime < %s AND end_datetime > %s
		""", (self.venue, self.name or "", self.end_datetime, self.start_datetime))
		if overlap:
			frappe.throw(_("Venue {0} is booked during this time (Event: {1})").format(
				self.venue, overlap[0][0]))

	def calculate_balance(self):
		self.balance = flt(self.total_amount) - flt(self.deposit_amount)
