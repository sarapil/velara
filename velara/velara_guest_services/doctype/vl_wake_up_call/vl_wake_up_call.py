# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
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
