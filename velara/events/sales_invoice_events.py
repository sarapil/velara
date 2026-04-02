"""VELARA — Sales Invoice doc_events (Invoice ↔ Folio sync)"""
import frappe
from frappe import _
from frappe.utils import flt


def on_submit(doc, method):
	"""When a hotel-linked Sales Invoice is submitted, update the folio."""
	if not doc.get("vl_folio"):
		return
	if not frappe.db.exists("DocType", "VL Folio"):
		return
	try:
		# Record the invoice amount as a charge on the folio
		from velara.utils import post_charge_to_folio
		post_charge_to_folio(
			doc.vl_folio, doc.get("vl_charge_type") or "Miscellaneous",
			flt(doc.grand_total),
			_("Invoice: {0}").format(doc.name),
			"Sales Invoice", doc.name
		)
		frappe.logger().info(f"VELARA: Invoice {doc.name} posted to folio {doc.vl_folio}")
	except Exception as e:
		frappe.log_error(f"VELARA Invoice Event Error: {str(e)}")


def on_cancel(doc, method):
	"""When a hotel-linked Sales Invoice is cancelled, reverse folio impact."""
	if not doc.get("vl_folio"):
		return
	try:
		# Void the related folio charge
		if frappe.db.exists("DocType", "VL Folio Charge"):
			charges = frappe.get_all("VL Folio Charge",
				filters={"folio": doc.vl_folio, "reference_type": "Sales Invoice",
					"reference_name": doc.name}, pluck="name")
			for charge in charges:
				frappe.db.set_value("VL Folio Charge", charge, "status", "Void")
		frappe.logger().info(f"VELARA: Invoice {doc.name} cancelled, folio charges voided")
	except Exception as e:
		frappe.log_error(f"VELARA Invoice Cancel Error: {str(e)}")
