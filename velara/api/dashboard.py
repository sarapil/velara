# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Dashboard API
Provides data for the VELARA visual dashboard screens.
"""
import frappe
from frappe import _
from frappe.utils import today, flt, cint, add_days, getdate


@frappe.whitelist()
def get_dashboard_stats():
	"""Get comprehensive dashboard statistics for VELARA Command Center."""
	frappe.has_permission("VL Room", "read", throw=True)

	stats = {}

	# Room Statistics
	if frappe.db.exists("DocType", "VL Room"):
		stats["rooms"] = {
			"total": frappe.db.count("VL Room", {"is_active": 1}),
			"occupied": frappe.db.count("VL Room", {"room_status": "Occupied", "is_active": 1}),
			"available": frappe.db.count("VL Room", {"room_status": "Available", "is_active": 1}),
			"dirty": frappe.db.count("VL Room", {"room_status": "Dirty", "is_active": 1}),
			"out_of_order": frappe.db.count("VL Room", {"room_status": "Out of Order", "is_active": 1}),
			"out_of_service": frappe.db.count("VL Room", {"room_status": "Out of Service", "is_active": 1}),
		}
		total = stats["rooms"]["total"] or 1
		stats["rooms"]["occupancy_pct"] = flt(stats["rooms"]["occupied"] / total * 100, 1)

	# Today's Operations
	if frappe.db.exists("DocType", "VL Reservation"):
		stats["today"] = {
			"arrivals": frappe.db.count("VL Reservation", {
				"check_in_date": today(),
				"status": ["in", ["Confirmed", "Guaranteed"]]
			}),
			"departures": frappe.db.count("VL Reservation", {
				"check_out_date": today(),
				"status": "Checked In"
			}),
			"in_house": frappe.db.count("VL Reservation", {"status": "Checked In"}),
		}

	# Revenue (today)
	if frappe.db.exists("DocType", "VL Folio Charge"):
		revenue = frappe.db.get_value(
			"VL Folio Charge",
			{"posting_date": today(), "status": ["!=", "Void"]},
			"sum(amount)"
		)
		stats["revenue_today"] = flt(revenue)

	# Housekeeping
	if frappe.db.exists("DocType", "VL HK Task"):
		stats["housekeeping"] = {
			"pending": frappe.db.count("VL HK Task", {"date": today(), "status": "Pending"}),
			"in_progress": frappe.db.count("VL HK Task", {"date": today(), "status": "In Progress"}),
			"completed": frappe.db.count("VL HK Task", {"date": today(), "status": "Completed"}),
		}

	# Guest Services
	if frappe.db.exists("DocType", "VL Service Request"):
		stats["service_requests"] = {
			"open": frappe.db.count("VL Service Request", {"status": "Open"}),
			"in_progress": frappe.db.count("VL Service Request", {"status": "In Progress"}),
		}

	# Maintenance
	if frappe.db.exists("DocType", "VL Maintenance Request"):
		stats["maintenance"] = {
			"open": frappe.db.count("VL Maintenance Request", {"status": "Open"}),
		}

	return stats


@frappe.whitelist()
def get_occupancy_trend(days=30):
	"""Get occupancy trend data for charts."""
	frappe.has_permission("VL Room", "read", throw=True)

	data = []
	total_rooms = frappe.db.count("VL Room", {"is_active": 1}) if frappe.db.exists("DocType", "VL Room") else 0

	if not total_rooms or not frappe.db.exists("DocType", "VL Night Audit"):
		return data

	audits = frappe.get_all(
		"VL Night Audit",
		filters={"audit_date": [">=", add_days(today(), -cint(days))]},
		fields=["audit_date", "occupied_rooms", "total_revenue", "adr", "revpar"],
		order_by="audit_date asc"
	)

	for audit in audits:
		data.append({
			"date": audit.audit_date,
			"occupancy": flt(audit.occupied_rooms / total_rooms * 100, 1) if total_rooms else 0,
			"revenue": flt(audit.total_revenue),
			"adr": flt(audit.adr),
			"revpar": flt(audit.revpar),
		})

	return data


@frappe.whitelist()
def get_room_status_map():
	"""Get room status data for the interactive room map."""
	frappe.has_permission("VL Room", "read", throw=True)

	if not frappe.db.exists("DocType", "VL Room"):
		return []

	rooms = frappe.get_all(
		"VL Room",
		filters={"is_active": 1},
		fields=[
			"name", "room_number", "room_type", "floor", "wing",
			"room_status", "current_guest", "current_reservation",
			"is_connecting", "connecting_room",
			"hk_status", "maintenance_status"
		],
		order_by="floor asc, room_number asc"
	)

	return rooms


@frappe.whitelist()
def get_arrivals_departures(date=None):
	"""Get detailed arrival and departure list for a specific date."""
	frappe.has_permission("VL Reservation", "read", throw=True)

	if not date:
		date = today()

	result = {"arrivals": [], "departures": []}

	if not frappe.db.exists("DocType", "VL Reservation"):
		return result

	result["arrivals"] = frappe.get_all(
		"VL Reservation",
		filters={
			"check_in_date": date,
			"status": ["in", ["Confirmed", "Guaranteed", "Tentative"]]
		},
		fields=[
			"name", "guest", "guest_name", "room_type", "room",
			"check_in_date", "check_out_date", "adults", "children",
			"rate_plan", "net_total", "special_requests", "booking_source"
		],
		order_by="guest_name asc"
	)

	result["departures"] = frappe.get_all(
		"VL Reservation",
		filters={
			"check_out_date": date,
			"status": "Checked In"
		},
		fields=[
			"name", "guest", "guest_name", "room",
			"check_out_date", "folio", "balance"
		],
		order_by="guest_name asc"
	)

	return result


@frappe.whitelist()
def get_dashboard_data():
	"""Flat dashboard data for the Velara Dashboard page.

	Combines stats, arrivals/departures, and housekeeping into a single
	response with the flat field names expected by the page JS.
	"""
	frappe.only_for(["VL User", "VL Manager", "System Manager"])

	stats = get_dashboard_stats()
	arrivals_departures = get_arrivals_departures()

	rooms = stats.get("rooms") or {}
	today_ops = stats.get("today") or {}
	hk = stats.get("housekeeping") or {}

	return {
		# Metrics row
		"total_rooms": rooms.get("total", 0),
		"occupied": rooms.get("occupied", 0),
		"available": rooms.get("available", 0),
		"occupancy_pct": rooms.get("occupancy_pct", 0),
		"arrivals_today": today_ops.get("arrivals", 0),
		"departures_today": today_ops.get("departures", 0),
		"revenue_today": stats.get("revenue_today", 0),
		"adr": flt(stats.get("revenue_today", 0) / (rooms.get("occupied", 0) or 1), 2),

		# Tables
		"arrivals": arrivals_departures.get("arrivals", []),
		"departures": arrivals_departures.get("departures", []),

		# Housekeeping summary
		"housekeeping": {
			"clean": rooms.get("available", 0),
			"dirty": rooms.get("dirty", 0),
			"in_progress": hk.get("in_progress", 0),
			"inspected": 0,
			"out_of_order": rooms.get("out_of_order", 0),
		},
	}
