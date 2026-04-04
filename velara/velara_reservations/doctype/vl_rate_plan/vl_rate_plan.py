# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Rate Plan — Rate Plan / Pricing Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VLRatePlan(Document):
	def validate(self):
		if flt(self.base_rate) <= 0:
			frappe.throw(_("Base Rate must be greater than zero"))
		if hasattr(self, 'min_rate') and hasattr(self, 'max_rate'):
			if flt(self.min_rate) > 0 and flt(self.max_rate) > 0:
				if flt(self.min_rate) > flt(self.max_rate):
					frappe.throw(_("Minimum Rate cannot exceed Maximum Rate"))
