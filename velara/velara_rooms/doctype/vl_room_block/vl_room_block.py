# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Room Block — Block rooms from inventory"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class VLRoomBlock(Document):
	def validate(self):
		self.validate_dates()
		self.validate_overlap()

	def after_insert(self):
		self.update_room_status()

	def on_trash(self):
		if self.room:
			frappe.db.set_value("VL Room", self.room, "room_status", "Available")

	def validate_dates(self):
		if not self.from_date or not self.to_date:
			frappe.throw(_("From Date and To Date are required"))
		if getdate(self.to_date) < getdate(self.from_date):
			frappe.throw(_("To Date cannot be before From Date"))

	def validate_overlap(self):
		overlap = frappe.db.sql("""
			SELECT name FROM `tabVL Room Block`
			WHERE room = %s AND name != %s
				AND from_date <= %s AND to_date >= %s
		""", (self.room, self.name or "", self.to_date, self.from_date))
		if overlap:
			frappe.throw(_("Room {0} is already blocked for overlapping dates (Block: {1})").format(
				self.room, overlap[0][0]))

	def update_room_status(self):
		if self.room:
			status = "Out of Order" if self.block_reason == "Maintenance" else "Out of Service"
			frappe.db.set_value("VL Room", self.room, "room_status", status)
