# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Lost and Found — Lost & Found Item Tracking"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class VLLostandFound(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLLF-.YYYY.-.#####", doc=self)

	def validate(self):
		if hasattr(self, 'found_date') and not self.found_date:
			self.found_date = today()
