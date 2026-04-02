# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Folio — Guest Folio / Bill Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class VLFolio(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLF-.YYYY.-.#####", doc=self)

	def validate(self):
		self.validate_guest()
		self.calculate_totals()

	def before_submit(self):
		if flt(self.balance) > 0:
			frappe.throw(_("Cannot submit folio with outstanding balance of {0}").format(
				self.balance))
		self.status = "Settled"

	def on_cancel(self):
		self.db_set("status", "Void")

	def validate_guest(self):
		if self.guest:
			self.guest_name = frappe.db.get_value("VL Guest", self.guest, "guest_name")

	def calculate_totals(self):
		"""Recalculate totals from child table charges."""
		total_charges = 0
		total_tax = 0
		total_payments = 0

		for row in self.charges or []:
			if row.charge_type == "Payment":
				total_payments += flt(row.amount)
			else:
				total_charges += flt(row.amount)
				total_tax += flt(row.tax_amount) if hasattr(row, 'tax_amount') else 0

		self.total_charges = flt(total_charges, 2)
		self.total_tax = flt(total_tax, 2)
		self.total_payments = flt(total_payments, 2)
		self.grand_total = flt(self.total_charges + self.total_tax, 2)
		self.paid_amount = flt(self.total_payments, 2)
		self.balance = flt(self.grand_total - self.paid_amount, 2)

	@frappe.whitelist()
	def post_charge(self, charge_type, amount, description=None):
		"""Post a charge to this folio."""
		frappe.only_for(["VL Manager", "System Manager"])

		row = self.append("charges", {})
		row.charge_type = charge_type
		row.amount = flt(amount)
		row.description = description or charge_type
		row.posting_date = today()
		self.save(ignore_permissions=True)
		return row.name

	@frappe.whitelist()
	def post_payment(self, amount, payment_method="Cash"):
		"""Record a payment against this folio."""
		frappe.only_for(["VL Manager", "System Manager"])

		row = self.append("charges", {})
		row.charge_type = "Payment"
		row.amount = flt(amount)
		row.description = _("Payment via {0}").format(payment_method)
		row.posting_date = today()
		self.save(ignore_permissions=True)
		return row.name

	@frappe.whitelist()
	def create_sales_invoice(self):
		"""Generate ERPNext Sales Invoice from folio charges."""
		frappe.only_for(["VL Manager", "System Manager"])

		if not self.guest:
			frappe.throw(_("Guest is required to create invoice"))

		customer = frappe.db.get_value("VL Guest", self.guest, "customer")
		if not customer:
			frappe.throw(_("Guest {0} has no linked Customer").format(self.guest))

		si = frappe.new_doc("Sales Invoice")
		si.customer = customer
		si.vl_folio = self.name
		si.vl_reservation = self.reservation
		si.vl_room = self.room

		for charge in self.charges or []:
			if charge.charge_type != "Payment" and flt(charge.amount) > 0:
				si.append("items", {
					"item_name": charge.description or charge.charge_type,
					"qty": 1,
					"rate": flt(charge.amount),
				})

		si.insert(ignore_permissions=True)
		return si.name
