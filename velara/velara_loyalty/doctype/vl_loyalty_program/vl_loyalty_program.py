# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Loyalty Program — Loyalty Configuration Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint


class VLLoyaltyProgram(Document):
	def validate(self):
		if hasattr(self, 'points_per_currency') and flt(self.points_per_currency) < 0:
			frappe.throw(_("Points per currency unit cannot be negative"))

	@staticmethod
	def calculate_points(amount):
		"""Calculate loyalty points for a given spend amount."""
		try:
			program = frappe.get_cached_doc("VL Loyalty Program")
			rate = flt(program.points_per_currency) if hasattr(program, 'points_per_currency') else 1
			return cint(flt(amount) * rate)
		except Exception:
			return 0
