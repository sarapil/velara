"""
VELARA — Uninstallation Scripts
"""
import frappe
from frappe import _


def before_uninstall():
	"""Pre-uninstallation cleanup."""
	_remove_custom_fields()


def after_uninstall():
	"""Post-uninstallation cleanup."""
	_remove_roles()
	frappe.db.commit()
	frappe.msgprint(_("VELARA Hotel Management uninstalled. 👋"))


def _remove_custom_fields():
	"""Remove custom fields added to ERPNext doctypes."""
	doctypes_fields = {
		"Customer": ["vl_section", "vl_guest", "vl_loyalty_tier",
					  "vl_total_stays", "vl_cb_1", "vl_vip_code", "vl_guest_preferences"],
		"Sales Invoice": ["vl_section", "vl_folio", "vl_reservation",
						   "vl_cb_1", "vl_room", "vl_charge_type"],
		"Employee": ["vl_section", "vl_hotel_department", "vl_property"],
	}

	for doctype, fieldnames in doctypes_fields.items():
		for fieldname in fieldnames:
			try:
				cf = frappe.db.get_value("Custom Field", {"dt": doctype, "fieldname": fieldname})
				if cf:
					frappe.delete_doc("Custom Field", cf, force=True)
			except Exception:
				pass


def _remove_roles():
	"""Remove VELARA roles."""
	roles = frappe.get_all("Role", filters={"name": ["like", "Velara%"]}, pluck="name")
	for role in roles:
		try:
			frappe.delete_doc("Role", role, force=True)
		except Exception:
			pass
