# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "total_rooms", "label": _("Total Rooms"), "fieldtype": "Int", "width": 100},
		{"fieldname": "occupied", "label": _("Occupied"), "fieldtype": "Int", "width": 100},
		{"fieldname": "available", "label": _("Available"), "fieldtype": "Int", "width": 100},
		{"fieldname": "occupancy_pct", "label": _("Occupancy %"), "fieldtype": "Percent", "width": 120},
		{"fieldname": "arrivals", "label": _("Arrivals"), "fieldtype": "Int", "width": 80},
		{"fieldname": "departures", "label": _("Departures"), "fieldtype": "Int", "width": 100},
	]


def get_data(filters):
	if not filters:
		filters = {}

	from_date = getdate(filters.get("from_date") or add_days(frappe.utils.today(), -30))
	to_date = getdate(filters.get("to_date") or frappe.utils.today())

	total_rooms = frappe.db.count("VL Room", {"room_status": ["!=", "Out of Service"]}) or 0
	data = []

	current = from_date
	while current <= to_date:
		date_str = str(current)

		occupied = frappe.db.count("VL Reservation", {
			"check_in_date": ["<=", date_str], "check_out_date": [">", date_str],
			"status": ["in", ["Confirmed", "Guaranteed", "Checked In"]],
			"docstatus": 1
		})

		arrivals = frappe.db.count("VL Reservation", {
			"check_in_date": date_str, "docstatus": 1,
			"status": ["not in", ["Cancelled", "No Show"]]
		})

		departures = frappe.db.count("VL Reservation", {
			"check_out_date": date_str, "docstatus": 1,
			"status": ["not in", ["Cancelled", "No Show"]]
		})

		available = total_rooms - occupied
		occ_pct = round(occupied / total_rooms * 100, 1) if total_rooms else 0

		data.append({
			"date": date_str,
			"total_rooms": total_rooms,
			"occupied": occupied,
			"available": available,
			"occupancy_pct": occ_pct,
			"arrivals": arrivals,
			"departures": departures,
		})

		current = add_days(current, 1)

	return data


def get_chart(data):
	labels = [d["date"] for d in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Occupancy %"), "values": [d["occupancy_pct"] for d in data]},
			]
		},
		"type": "line",
		"colors": ["#C9A84C"],
	}
