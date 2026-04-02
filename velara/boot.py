"""
VELARA - Hotel & Hospitality Management System
نظام إدارة الفنادق والضيافة
"""
import frappe


def boot_session(bootinfo):
	"""Inject VELARA configuration into the boot session."""
	if frappe.session.user == "Guest":
		return

	bootinfo.velara = frappe._dict()

	# Check if user has any Velara roles
	user_roles = frappe.get_roles(frappe.session.user)
	velara_roles = [r for r in user_roles if r.startswith("Velara")]

	bootinfo.velara.has_access = bool(velara_roles) or "System Manager" in user_roles
	bootinfo.velara.roles = velara_roles

	if not bootinfo.velara.has_access:
		return

	# App feature flags (controlled via VL Settings)
	bootinfo.velara.features = _get_feature_flags()

	# Quick stats for dashboard
	bootinfo.velara.stats = _get_quick_stats()

	# User's property assignment (multi-property support)
	bootinfo.velara.property = _get_user_property()


def _get_feature_flags():
	"""Get module enable/disable flags from VL Settings."""
	defaults = {
		"rooms_enabled": True,
		"reservations_enabled": True,
		"front_desk_enabled": True,
		"housekeeping_enabled": True,
		"fnb_enabled": True,
		"revenue_enabled": True,
		"guest_services_enabled": True,
		"events_enabled": True,
		"maintenance_enabled": True,
		"loyalty_enabled": True,
		"night_audit_enabled": True,
		"spa_enabled": False,
		"iot_enabled": False,
		"channel_manager_enabled": False,
		"visual_dashboard": True,
	}

	if not frappe.db.exists("DocType", "VL Settings"):
		return defaults

	try:
		settings = frappe.get_cached_doc("VL Settings")
		for key in defaults:
			if hasattr(settings, key):
				defaults[key] = getattr(settings, key)
	except Exception:
		pass

	return defaults


def _get_quick_stats():
	"""Get quick stats for the boot session."""
	stats = {}

	try:
		if frappe.db.exists("DocType", "VL Room"):
			stats["total_rooms"] = frappe.db.count("VL Room")
			stats["occupied_rooms"] = frappe.db.count("VL Room", {"status": "Occupied"})
			stats["available_rooms"] = frappe.db.count("VL Room", {"status": "Available"})

		if frappe.db.exists("DocType", "VL Reservation"):
			today = frappe.utils.today()
			stats["arrivals_today"] = frappe.db.count("VL Reservation", {
				"check_in_date": today,
				"status": ["in", ["Confirmed", "Guaranteed"]]
			})
			stats["departures_today"] = frappe.db.count("VL Reservation", {
				"check_out_date": today,
				"status": "Checked In"
			})

		if frappe.db.exists("DocType", "VL Guest"):
			stats["in_house_guests"] = frappe.db.count("VL Guest", {"status": "In House"})

	except Exception:
		pass

	return stats


def _get_user_property():
	"""Get the property assigned to the current user."""
	try:
		if frappe.db.exists("DocType", "VL Property"):
			# Check if user is assigned to a specific property
			property_name = frappe.db.get_value(
				"VL Property",
				{"default_user": frappe.session.user},
				"name"
			)
			if property_name:
				return property_name

			# If only one property exists, use it
			properties = frappe.db.get_all("VL Property", limit=2)
			if len(properties) == 1:
				return properties[0].name
	except Exception:
		pass

	return None
