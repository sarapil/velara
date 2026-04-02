# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Service Request — Guest Service Request Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


class VLServiceRequest(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLSR-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.requested_at:
			self.requested_at = now_datetime()

	def on_update(self):
		if self.status == "Completed" and not self.completed_at:
			self.db_set("completed_at", now_datetime())
		if self.status == "Completed" and self.is_chargeable and flt(self.charge_amount) > 0:
			self.post_to_folio()

	def post_to_folio(self):
		if self.folio and not self.flags.charge_posted:
			from velara.utils import post_charge_to_folio
			post_charge_to_folio(
				self.folio, "Service", self.charge_amount,
				self.description or self.request_type,
				"VL Service Request", self.name
			)
			self.flags.charge_posted = True

	@frappe.whitelist()
	def resolve(self, resolution_notes=None):
		frappe.only_for(["VL User", "VL Manager", "System Manager"])

		self.status = "Completed"
		self.completed_at = now_datetime()
		self.save(ignore_permissions=True)
