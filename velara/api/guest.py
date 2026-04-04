# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Guest API
"""
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def get_guest_profile(guest):
	"""Get comprehensive guest profile (Guest 360° view)."""
	frappe.has_permission("VL Guest", "read", throw=True)

	if not frappe.db.exists("VL Guest", guest):
		frappe.throw(_("Guest {0} not found").format(guest))

	profile = frappe.get_doc("VL Guest", guest).as_dict()

	# Stay history
	if frappe.db.exists("DocType", "VL Reservation"):
		profile["stay_history"] = frappe.get_all(
			"VL Reservation",
			filters={"guest": guest},
			fields=["name", "room", "room_type", "check_in_date", "check_out_date",
					 "status", "total_amount", "source"],
			order_by="check_in_date desc",
			limit=20
		)
		profile["total_stays"] = len(profile["stay_history"])
		profile["total_revenue"] = flt(sum(s.total_amount or 0 for s in profile["stay_history"]))

	# Current stay
	if frappe.db.exists("DocType", "VL Reservation"):
		current = frappe.get_all(
			"VL Reservation",
			filters={"guest": guest, "status": "Checked In"},
			fields=["name", "room", "check_in_date", "check_out_date", "folio"],
			limit=1
		)
		profile["current_stay"] = current[0] if current else None

	# Preferences
	if frappe.db.exists("DocType", "VL Guest Preference"):
		profile["preferences"] = frappe.get_all(
			"VL Guest Preference",
			filters={"guest": guest},
			fields=["preference_type", "preference_value", "notes"]
		)

	# Feedback
	if frappe.db.exists("DocType", "VL Guest Feedback"):
		profile["feedback"] = frappe.get_all(
			"VL Guest Feedback",
			filters={"guest": guest},
			fields=["name", "rating", "feedback_type", "comments", "creation"],
			order_by="creation desc",
			limit=10
		)

	# Loyalty
	if frappe.db.exists("DocType", "VL Loyalty Program"):
		profile["loyalty"] = {
			"tier": profile.get("loyalty_tier"),
			"points": profile.get("loyalty_points", 0),
		}

	return profile


@frappe.whitelist()
def search_guest(query):
	"""Search guests by name, email, phone, or ID."""
	frappe.has_permission("VL Guest", "read", throw=True)

	if not query or len(query) < 2:
		return []

	return frappe.get_all(
		"VL Guest",
		filters={
			"name": ["like", f"%{query}%"]
		},
		or_filters={
			"guest_name": ["like", f"%{query}%"],
			"email": ["like", f"%{query}%"],
			"mobile": ["like", f"%{query}%"],
			"id_number": ["like", f"%{query}%"],
		},
		fields=["name", "guest_name", "email", "mobile", "nationality",
				 "vip_code", "loyalty_tier", "status"],
		limit=20,
		order_by="guest_name asc"
	)
