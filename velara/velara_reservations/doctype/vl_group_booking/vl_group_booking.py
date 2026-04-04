# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Group Booking — Group/Block Reservation Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class VLGroupBooking(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLGB-.YYYY.-.#####", doc=self)

	def validate(self):
		self.update_room_count()

	def update_room_count(self):
		"""Count linked reservations."""
		if not self.is_new():
			count = frappe.db.count("VL Reservation", {"group_booking": self.name, "docstatus": ["<", 2]})
			if hasattr(self, 'rooms_blocked'):
				self.rooms_blocked = cint(count)
