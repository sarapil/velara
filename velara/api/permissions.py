# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Permission API
"""
import frappe


@frappe.whitelist(allow_guest=True)
def has_app_permission():
	"""Check if the current user has permission to access VELARA."""
	if frappe.session.user == "Guest":
		return False

	user_roles = frappe.get_roles(frappe.session.user)

	if "System Manager" in user_roles or "Administrator" in user_roles:
		return True

	velara_roles = [r for r in user_roles if r.startswith("Velara")]
	return bool(velara_roles)
