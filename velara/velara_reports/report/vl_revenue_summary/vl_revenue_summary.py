# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "room_revenue", "label": _("Room Revenue"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "fnb_revenue", "label": _("F&B Revenue"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "spa_revenue", "label": _("Spa Revenue"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "other_revenue", "label": _("Other Revenue"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_revenue", "label": _("Total Revenue"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "adr", "label": _("ADR"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "revpar", "label": _("RevPAR"), "fieldtype": "Currency", "width": 100},
	]


def get_data(filters):
	if not filters:
		filters = {}

	from_date = getdate(filters.get("from_date") or add_days(frappe.utils.today(), -30))
	to_date = getdate(filters.get("to_date") or frappe.utils.today())

	audits = frappe.get_all("VL Night Audit",
		filters={
			"audit_date": ["between", [from_date, to_date]],
			"docstatus": 1
		},
		fields=["audit_date as date", "room_revenue", "fnb_revenue", "other_revenue",
			"total_revenue", "adr", "revpar", "occupied_rooms", "total_rooms"],
		order_by="audit_date asc")

	for row in audits:
		row["spa_revenue"] = 0  # Will be populated when spa revenue is tracked separately

	return audits


def get_chart(data):
	if not data:
		return None
	return {
		"data": {
			"labels": [str(d["date"]) for d in data],
			"datasets": [
				{"name": _("Total Revenue"), "values": [flt(d["total_revenue"]) for d in data]},
				{"name": _("Room Revenue"), "values": [flt(d["room_revenue"]) for d in data]},
			]
		},
		"type": "bar",
		"colors": ["#C9A84C", "#1B2A4A"],
	}
