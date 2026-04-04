# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VELARA — Payment Entry doc_events (Payment ↔ Folio settlement)"""
import frappe
from frappe import _
from frappe.utils import flt


def on_submit(doc, method):
	"""When a hotel-linked Payment Entry is submitted, update folio paid amount."""
	# Check if this payment is linked to a VELARA folio via references
	for ref in doc.get("references", []):
		if ref.reference_doctype == "Sales Invoice":
			vl_folio = frappe.db.get_value("Sales Invoice", ref.reference_name, "vl_folio")
			if vl_folio:
				_update_folio_payment(vl_folio, flt(ref.allocated_amount))


def on_cancel(doc, method):
	"""When a hotel-linked Payment Entry is cancelled, reverse folio payment."""
	for ref in doc.get("references", []):
		if ref.reference_doctype == "Sales Invoice":
			vl_folio = frappe.db.get_value("Sales Invoice", ref.reference_name, "vl_folio")
			if vl_folio:
				_update_folio_payment(vl_folio, -flt(ref.allocated_amount))


def _update_folio_payment(folio, amount):
	"""Update folio paid amount."""
	if not frappe.db.exists("DocType", "VL Folio"):
		return

	try:
		current_paid = flt(frappe.db.get_value("VL Folio", folio, "paid_amount"))
		new_paid = current_paid + amount
		total = flt(frappe.db.get_value("VL Folio", folio, "total_amount"))

		frappe.db.set_value("VL Folio", folio, {
			"paid_amount": new_paid,
			"balance": total - new_paid,
		})
	except Exception as e:
		frappe.log_error(f"VELARA Folio Payment Update Error: {str(e)}")
