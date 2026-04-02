# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Guest Feedback — Guest Review & Feedback Controller"""

import frappe
from frappe import _
from frappe.model.document import Document


class VLGuestFeedback(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLGF-.YYYY.-.#####", doc=self)

	def after_insert(self):
		"""Alert management for low ratings."""
		if hasattr(self, 'overall_rating') and self.overall_rating and self.overall_rating <= 2:
			frappe.publish_realtime("vl_low_rating", {
				"guest": self.guest, "rating": self.overall_rating, "feedback": self.name
			})
