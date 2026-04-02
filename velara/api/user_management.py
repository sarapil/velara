"""
VELARA — User Management API
Provides a unified visual interface for managing hotel staff roles and CAPS.
"""
import frappe
from frappe import _


@frappe.whitelist()
def get_hotel_staff():
	"""Get all hotel staff with their VELARA roles."""
	frappe.only_for(["System Manager", "Velara Admin", "Velara General Manager"])

	staff = []
	velara_roles = frappe.get_all("Role", filters={"name": ["like", "Velara%"]}, pluck="name")

	users_with_roles = frappe.get_all(
		"Has Role",
		filters={"role": ["in", velara_roles]},
		fields=["parent", "role"],
	)

	# Group by user
	user_roles = {}
	for ur in users_with_roles:
		user_roles.setdefault(ur.parent, []).append(ur.role)

	for user, roles in user_roles.items():
		user_info = frappe.get_value("User", user,
			["full_name", "email", "user_image", "enabled"], as_dict=True)
		if user_info:
			staff.append({
				"user": user,
				"full_name": user_info.full_name,
				"email": user_info.email,
				"image": user_info.user_image,
				"enabled": user_info.enabled,
				"roles": roles,
			})

	return staff


@frappe.whitelist()
def assign_role(user, role):
	"""Assign a VELARA role to a user."""
	frappe.only_for(["System Manager", "Velara Admin"])

	if not role.startswith("Velara"):
		frappe.throw(_("Can only assign Velara roles"))

	user_doc = frappe.get_doc("User", user)
	existing = [r.role for r in user_doc.roles]

	if role not in existing:
		user_doc.append("roles", {"role": role})
		user_doc.save(ignore_permissions=True)

	return {"success": True}


@frappe.whitelist()
def remove_role(user, role):
	"""Remove a VELARA role from a user."""
	frappe.only_for(["System Manager", "Velara Admin"])

	if not role.startswith("Velara"):
		frappe.throw(_("Can only remove Velara roles"))

	user_doc = frappe.get_doc("User", user)
	user_doc.roles = [r for r in user_doc.roles if r.role != role]
	user_doc.save(ignore_permissions=True)

	return {"success": True}
