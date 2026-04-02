# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL HK Assignment — Housekeeper Daily Assignment"""

import frappe
from frappe import _
from frappe.model.document import Document


class VLHKAssignment(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLHA-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.housekeeper:
			frappe.throw(_("Housekeeper is required"))
		if not self.assignment_date:
			self.assignment_date = frappe.utils.today()
		self.update_task_counts()

	def update_task_counts(self):
		"""Count assigned/completed tasks for this housekeeper on this date."""
		if self.housekeeper and self.assignment_date:
			total = frappe.db.count("VL HK Task", {
				"assigned_to": self.housekeeper,
				"scheduled_date": self.assignment_date,
			})
			completed = frappe.db.count("VL HK Task", {
				"assigned_to": self.housekeeper,
				"scheduled_date": self.assignment_date,
				"status": ["in", ["Completed", "Inspected"]],
			})
			self.rooms_assigned = total
			self.rooms_completed = completed
