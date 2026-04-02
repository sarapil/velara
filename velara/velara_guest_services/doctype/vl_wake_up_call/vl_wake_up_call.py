# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Wake Up Call — Wake-up Call Scheduling Controller"""

import frappe
from frappe import _
from frappe.model.document import Document


class VLWakeUpCall(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLWU-.YYYY.-.#####", doc=self)

	def validate(self):
		if hasattr(self, 'wake_time') and not self.wake_time:
			frappe.throw(_("Wake-up time is required"))
