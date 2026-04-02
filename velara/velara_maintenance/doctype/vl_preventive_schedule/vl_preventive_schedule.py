# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Preventive Schedule — Preventive Maintenance Scheduling"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, today, getdate


class VLPreventiveSchedule(Document):
	def validate(self):
		if not hasattr(self, 'next_due_date') or not self.next_due_date:
			self.next_due_date = today()

	def calculate_next_due(self):
		"""Calculate next due date based on frequency."""
		if not hasattr(self, 'frequency'):
			return
		freq_map = {
			"Daily": lambda d: add_days(d, 1),
			"Weekly": lambda d: add_days(d, 7),
			"Biweekly": lambda d: add_days(d, 14),
			"Monthly": lambda d: add_months(d, 1),
			"Quarterly": lambda d: add_months(d, 3),
			"Semi-Annual": lambda d: add_months(d, 6),
			"Annual": lambda d: add_months(d, 12),
		}
		calc = freq_map.get(self.frequency)
		if calc:
			self.next_due_date = calc(getdate(self.next_due_date or today()))
			self.save(ignore_permissions=True)
