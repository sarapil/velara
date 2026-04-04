# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Installation Scripts
"""
import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def before_install():
	"""Pre-installation checks."""
	pass


def after_install():
	"""Post-installation setup."""
	create_roles()
	create_settings()
	create_custom_fields_on_erpnext()
	# ── Desktop Icon injection (Frappe v16 /desk) ──
	from velara.desktop_utils import inject_app_desktop_icon
	inject_app_desktop_icon(
	    app="velara",
	    label="VELARA",
	    route="/app/velara",
	    logo_url="/assets/velara/images/velara-logo.svg",
	    bg_color="#C9A84C",
	)
	frappe.db.commit()
	frappe.msgprint(_("VELARA Hotel Management installed successfully! 🏨"))


def create_roles():
	"""Create default VELARA roles."""
	roles = [
		{"role_name": "Velara Admin", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara General Manager", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Front Desk Manager", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Front Desk Agent", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Housekeeping Manager", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Housekeeper", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Revenue Manager", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara FnB Manager", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Concierge", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Maintenance Tech", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Events Coordinator", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Spa Manager", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Night Auditor", "desk_access": 1, "is_custom": 1},
		{"role_name": "Velara Viewer", "desk_access": 1, "is_custom": 1},
	]

	for role_data in roles:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.new_doc("Role")
			role.update(role_data)
			role.insert(ignore_permissions=True)
			frappe.logger().info(f"Created role: {role_data['role_name']}")


def create_settings():
	"""Create singleton VL Settings record."""
	if frappe.db.exists("DocType", "VL Settings"):
		if not frappe.db.exists("VL Settings", "VL Settings"):
			settings = frappe.new_doc("VL Settings")
			settings.insert(ignore_permissions=True)


def create_custom_fields_on_erpnext():
	"""Add custom fields to existing ERPNext/HRMS doctypes for hotel integration."""
	custom_fields = {
		"Customer": [
			{
				"fieldname": "vl_section",
				"label": "VELARA Guest Info",
				"fieldtype": "Section Break",
				"insert_after": "website",
				"collapsible": 1,
			},
			{
				"fieldname": "vl_guest",
				"label": "Guest Profile",
				"fieldtype": "Link",
				"options": "VL Guest",
				"insert_after": "vl_section",
			},
			{
				"fieldname": "vl_loyalty_tier",
				"label": "Loyalty Tier",
				"fieldtype": "Link",
				"options": "VL Loyalty Tier",
				"insert_after": "vl_guest",
				"read_only": 1,
			},
			{
				"fieldname": "vl_total_stays",
				"label": "Total Stays",
				"fieldtype": "Int",
				"insert_after": "vl_loyalty_tier",
				"read_only": 1,
			},
			{
				"fieldname": "vl_cb_1",
				"fieldtype": "Column Break",
				"insert_after": "vl_total_stays",
			},
			{
				"fieldname": "vl_vip_code",
				"label": "VIP Code",
				"fieldtype": "Select",
				"options": "\nNone\nVIP 1\nVIP 2\nVIP 3\nCelebrity\nBlacklist",
				"insert_after": "vl_cb_1",
			},
			{
				"fieldname": "vl_guest_preferences",
				"label": "Guest Preferences",
				"fieldtype": "Small Text",
				"insert_after": "vl_vip_code",
				"read_only": 1,
			},
		],
		"Sales Invoice": [
			{
				"fieldname": "vl_section",
				"label": "VELARA Hotel",
				"fieldtype": "Section Break",
				"insert_after": "remarks",
				"collapsible": 1,
			},
			{
				"fieldname": "vl_folio",
				"label": "Guest Folio",
				"fieldtype": "Link",
				"options": "VL Folio",
				"insert_after": "vl_section",
			},
			{
				"fieldname": "vl_reservation",
				"label": "Reservation",
				"fieldtype": "Link",
				"options": "VL Reservation",
				"insert_after": "vl_folio",
			},
			{
				"fieldname": "vl_cb_1",
				"fieldtype": "Column Break",
				"insert_after": "vl_reservation",
			},
			{
				"fieldname": "vl_room",
				"label": "Room",
				"fieldtype": "Link",
				"options": "VL Room",
				"insert_after": "vl_cb_1",
			},
			{
				"fieldname": "vl_charge_type",
				"label": "Hotel Charge Type",
				"fieldtype": "Select",
				"options": "\nRoom Charge\nF&B\nMinibar\nLaundry\nSpa\nParking\nDamage\nMiscellaneous",
				"insert_after": "vl_room",
			},
		],
		"Employee": [
			{
				"fieldname": "vl_section",
				"label": "VELARA Hotel",
				"fieldtype": "Section Break",
				"insert_after": "company_email",
				"collapsible": 1,
			},
			{
				"fieldname": "vl_hotel_department",
				"label": "Hotel Department",
				"fieldtype": "Select",
				"options": "\nFront Office\nHousekeeping\nFood & Beverage\nKitchen\nMaintenance\nSpa & Wellness\nEvents & Banquets\nConcierge\nSecurity\nAccounting\nManagement",
				"insert_after": "vl_section",
			},
			{
				"fieldname": "vl_property",
				"label": "Assigned Property",
				"fieldtype": "Link",
				"options": "VL Property",
				"insert_after": "vl_hotel_department",
			},
		],
	}

	try:
		create_custom_fields(custom_fields, update=True)
	except Exception:
		frappe.log_error("VELARA: Error creating custom fields")
