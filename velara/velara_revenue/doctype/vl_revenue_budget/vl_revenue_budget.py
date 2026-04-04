# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Revenue Budget — Revenue Budgeting & Forecasting"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VLRevenueBudget(Document):
	def validate(self):
		if hasattr(self, 'budgeted_amount') and flt(self.budgeted_amount) < 0:
			frappe.throw(_("Budget amount cannot be negative"))

	def calculate_variance(self):
		"""Calculate variance between budget and actual."""
		if hasattr(self, 'actual_amount') and hasattr(self, 'budgeted_amount'):
			self.variance = flt(self.actual_amount) - flt(self.budgeted_amount)
			self.variance_percent = (
				flt(self.variance / self.budgeted_amount * 100, 1)
				if flt(self.budgeted_amount) else 0
			)
