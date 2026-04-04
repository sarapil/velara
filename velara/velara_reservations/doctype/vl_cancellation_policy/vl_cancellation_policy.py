# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Cancellation Policy — Reservation Cancellation Rules"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VLCancellationPolicy(Document):
	def validate(self):
		if hasattr(self, 'charge_percent') and flt(self.charge_percent) > 100:
			frappe.throw(_("Cancellation charge percentage cannot exceed 100%"))
