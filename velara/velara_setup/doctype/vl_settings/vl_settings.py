# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Settings — Global Hotel Management Settings"""

import frappe
from frappe import _
from frappe.model.document import Document


class VLSettings(Document):
	def validate(self):
		self.validate_checkout_time()

	def validate_checkout_time(self):
		if hasattr(self, 'default_checkout_time') and hasattr(self, 'default_checkin_time'):
			pass  # Times are valid Select/Time fields

	@staticmethod
	def get_settings():
		"""Get cached settings singleton."""
		return frappe.get_cached_doc("VL Settings")
