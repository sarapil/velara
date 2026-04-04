# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Room — Room Management Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class VLRoom(Document):
	def autoname(self):
		if self.room_number and self.property:
			prop_abbr = frappe.db.get_value("VL Property", self.property, "abbreviation") or ""
			self.name = f"{prop_abbr}-{self.room_number}".strip("-")
		elif self.room_number:
			self.name = self.room_number

	def validate(self):
		self.validate_room_number()
		self.set_room_name()
		self.log_status_change()

	def validate_room_number(self):
		if not self.room_number:
			frappe.throw(_("Room Number is required"))

	def set_room_name(self):
		if not self.room_name:
			rt = self.room_type or ""
			self.room_name = f"{rt} - {self.room_number}".strip(" -")

	def log_status_change(self):
		"""Create a VL Room Status Log entry on status change."""
		if not self.is_new() and self.has_value_changed("room_status"):
			old = self.get_doc_before_save()
			if old and frappe.db.exists("DocType", "VL Room Status Log"):
				log = frappe.new_doc("VL Room Status Log")
				log.room = self.name
				log.from_status = old.room_status
				log.to_status = self.room_status
				log.changed_at = now_datetime()
				log.changed_by = frappe.session.user
				log.insert(ignore_permissions=True)

	@frappe.whitelist()
	def change_status(self, new_status, reason=None):
		"""Change room status with logging."""
		frappe.only_for(["VL Manager", "System Manager"])

		self.room_status = new_status
		self.save(ignore_permissions=True)
		return self.room_status
