"""VELARA — Customer doc_events (ERPNext Customer ↔ VL Guest sync)"""
import frappe
from frappe import _


def after_insert(doc, method):
	"""When a new Customer is created externally, optionally link to guest."""
	if not frappe.db.exists("DocType", "VL Guest"):
		return
	# If customer was created from VL Guest, the link is already set
	if doc.get("vl_guest"):
		return
	# Check if a VL Guest with same email exists for auto-linking
	if doc.get("email_id"):
		guest = frappe.db.get_value("VL Guest", {"email": doc.email_id}, "name")
		if guest:
			doc.db_set("vl_guest", guest)
			frappe.db.set_value("VL Guest", guest, "customer", doc.name)


def on_update(doc, method):
	"""Sync Customer changes to linked VL Guest profile."""
	if not frappe.db.exists("DocType", "VL Guest"):
		return
	if doc.get("vl_guest"):
		try:
			guest = frappe.get_doc("VL Guest", doc.vl_guest)
			updated = False
			if guest.guest_name != doc.customer_name:
				guest.guest_name = doc.customer_name
				updated = True
			if doc.get("email_id") and guest.email != doc.email_id:
				guest.email = doc.email_id
				updated = True
			if doc.get("mobile_no") and guest.mobile != doc.mobile_no:
				guest.mobile = doc.mobile_no
				updated = True
			if updated:
				guest.flags.ignore_validate = True
				guest.save(ignore_permissions=True)
		except Exception:
			frappe.log_error("VELARA: Error syncing Customer to Guest")
