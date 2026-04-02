# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL HK Task — Housekeeping Task Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds


class VLHKTask(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLHK-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.room:
			frappe.throw(_("Room is required"))
		if not self.scheduled_date:
			self.scheduled_date = now_datetime().date()
		if self.room:
			self.floor = frappe.db.get_value("VL Room", self.room, "floor")

	def on_update(self):
		self.update_room_hk_status()
		self.calculate_duration()

	def update_room_hk_status(self):
		hk_map = {
			"Pending": "Dirty", "Assigned": "Dirty", "In Progress": "Dirty",
			"Completed": "Clean", "Inspected": "Inspected",
		}
		hk_status = hk_map.get(self.status)
		if hk_status and self.room:
			frappe.db.set_value("VL Room", self.room, "housekeeping_status", hk_status)

	def calculate_duration(self):
		if self.started_at and self.completed_at:
			secs = time_diff_in_seconds(self.completed_at, self.started_at)
			self.db_set("duration_minutes", max(1, int(secs / 60)))

	@frappe.whitelist()
	def start_cleaning(self):
		frappe.only_for(["VL Manager", "System Manager"])

		self.status = "In Progress"
		self.started_at = now_datetime()
		self.save(ignore_permissions=True)

	@frappe.whitelist()
	def complete_cleaning(self):
		frappe.only_for(["VL Manager", "System Manager"])

		self.status = "Completed"
		self.completed_at = now_datetime()
		self.save(ignore_permissions=True)

	@frappe.whitelist()
	def pass_inspection(self, inspector=None):
		frappe.only_for(["VL User", "VL Manager", "System Manager"])

		self.status = "Inspected"
		self.inspected_by = inspector or frappe.session.user
		self.save(ignore_permissions=True)
		if self.room:
			frappe.db.set_value("VL Room", self.room, {
				"housekeeping_status": "Inspected", "room_status": "Available"
			})
