# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Loyalty Transaction — Points Earn/Redeem Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, today


class VLLoyaltyTransaction(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLLT-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.posting_date:
			self.posting_date = today()
		if cint(self.points) <= 0:
			frappe.throw(_("Points must be greater than zero"))
		if self.transaction_type == "Redeem":
			self.validate_sufficient_points()

	def after_insert(self):
		self.update_guest_points()

	def on_trash(self):
		self.revert_guest_points()

	def validate_sufficient_points(self):
		if self.guest:
			current = cint(frappe.db.get_value("VL Guest", self.guest, "loyalty_points"))
			if cint(self.points) > current:
				frappe.throw(_("Guest has only {0} points, cannot redeem {1}").format(
					current, self.points))

	def update_guest_points(self):
		if not self.guest:
			return
		delta = cint(self.points) if self.transaction_type == "Earn" else -cint(self.points)
		current = cint(frappe.db.get_value("VL Guest", self.guest, "loyalty_points"))
		frappe.db.set_value("VL Guest", self.guest, "loyalty_points", current + delta)

	def revert_guest_points(self):
		if not self.guest:
			return
		delta = -cint(self.points) if self.transaction_type == "Earn" else cint(self.points)
		current = cint(frappe.db.get_value("VL Guest", self.guest, "loyalty_points"))
		frappe.db.set_value("VL Guest", self.guest, "loyalty_points", max(0, current + delta))
