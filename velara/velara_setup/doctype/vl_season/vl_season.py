# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Season — Rate Season Definition"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, flt


class VLSeason(Document):
	def validate(self):
		if hasattr(self, 'start_date') and hasattr(self, 'end_date'):
			if self.start_date and self.end_date:
				if getdate(self.end_date) < getdate(self.start_date):
					frappe.throw(_("End Date cannot be before Start Date"))
		if hasattr(self, 'rate_multiplier'):
			if flt(self.rate_multiplier) <= 0:
				frappe.throw(_("Rate Multiplier must be greater than zero"))
