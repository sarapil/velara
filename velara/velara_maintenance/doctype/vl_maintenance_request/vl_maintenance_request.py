# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Maintenance Request — Maintenance Work Order Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, today


class VLMaintenanceRequest(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLMR-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.reported_date:
			self.reported_date = today()
		if not self.reported_by:
			self.reported_by = frappe.session.user

	def on_update(self):
		if self.status == "In Progress" and not self.started_at:
			self.db_set("started_at", now_datetime())
		if self.status == "Completed" and not self.completed_at:
			self.db_set("completed_at", now_datetime())
		self.update_room_if_needed()

	def update_room_if_needed(self):
		if self.room and self.status == "In Progress":
			frappe.db.set_value("VL Room", self.room, "room_status", "Out of Order")
		elif self.room and self.status == "Completed":
			frappe.db.set_value("VL Room", self.room, "room_status", "Dirty")

	@frappe.whitelist()
	def start_work(self):
		self.status = "In Progress"
		self.started_at = now_datetime()
		self.save(ignore_permissions=True)

	@frappe.whitelist()
	def complete_work(self, notes=None):
		self.status = "Completed"
		self.completed_at = now_datetime()
		if notes:
			self.resolution_notes = notes
		self.save(ignore_permissions=True)
