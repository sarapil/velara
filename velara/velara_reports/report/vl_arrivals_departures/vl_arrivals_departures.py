# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "reservation", "label": _("Reservation"), "fieldtype": "Link", "options": "VL Reservation", "width": 160},
		{"fieldname": "guest_name", "label": _("Guest Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "room", "label": _("Room"), "fieldtype": "Link", "options": "VL Room", "width": 100},
		{"fieldname": "room_type", "label": _("Room Type"), "fieldtype": "Data", "width": 130},
		{"fieldname": "check_in_date", "label": _("Check In"), "fieldtype": "Date", "width": 110},
		{"fieldname": "check_out_date", "label": _("Check Out"), "fieldtype": "Date", "width": 110},
		{"fieldname": "nights", "label": _("Nights"), "fieldtype": "Int", "width": 70},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "type", "label": _("Type"), "fieldtype": "Data", "width": 90},
		{"fieldname": "vip_code", "label": _("VIP"), "fieldtype": "Data", "width": 80},
	]


def get_data(filters):
	if not filters:
		filters = {}

	date = filters.get("date") or frappe.utils.today()
	data = []

	# Arrivals
	arrivals = frappe.get_all("VL Reservation",
		filters={
			"check_in_date": date,
			"status": ["in", ["Confirmed", "Guaranteed"]],
			"docstatus": 1
		},
		fields=["name as reservation", "guest_name", "room", "room_type",
			"check_in_date", "check_out_date", "nights", "status"])

	for a in arrivals:
		a["type"] = _("Arrival")
		vip = frappe.db.get_value("VL Guest", {"guest_name": a["guest_name"]}, "vip_code")
		a["vip_code"] = vip or ""
		data.append(a)

	# Departures
	departures = frappe.get_all("VL Reservation",
		filters={
			"check_out_date": date,
			"status": "Checked In",
			"docstatus": 1
		},
		fields=["name as reservation", "guest_name", "room", "room_type",
			"check_in_date", "check_out_date", "nights", "status"])

	for d in departures:
		d["type"] = _("Departure")
		data.append(d)

	# In-House
	in_house = frappe.get_all("VL Reservation",
		filters={
			"check_in_date": ["<", date],
			"check_out_date": [">", date],
			"status": "Checked In",
			"docstatus": 1
		},
		fields=["name as reservation", "guest_name", "room", "room_type",
			"check_in_date", "check_out_date", "nights", "status"])

	for ih in in_house:
		ih["type"] = _("In-House")
		data.append(ih)

	return data
