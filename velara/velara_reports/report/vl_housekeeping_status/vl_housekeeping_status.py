# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"fieldname": "room", "label": _("Room"), "fieldtype": "Link", "options": "VL Room", "width": 100},
		{"fieldname": "floor", "label": _("Floor"), "fieldtype": "Data", "width": 80},
		{"fieldname": "room_type", "label": _("Room Type"), "fieldtype": "Data", "width": 130},
		{"fieldname": "room_status", "label": _("Room Status"), "fieldtype": "Data", "width": 120},
		{"fieldname": "hk_status", "label": _("HK Status"), "fieldtype": "Data", "width": 120},
		{"fieldname": "current_guest", "label": _("Current Guest"), "fieldtype": "Link", "options": "VL Guest", "width": 140},
		{"fieldname": "hk_task", "label": _("HK Task"), "fieldtype": "Link", "options": "VL HK Task", "width": 140},
		{"fieldname": "assigned_to", "label": _("Assigned To"), "fieldtype": "Data", "width": 130},
		{"fieldname": "task_status", "label": _("Task Status"), "fieldtype": "Data", "width": 110},
	]


def get_data(filters):
	if not filters:
		filters = {}

	room_filters = {}
	if filters.get("floor"):
		room_filters["floor"] = filters["floor"]
	if filters.get("room_status"):
		room_filters["room_status"] = filters["room_status"]

	rooms = frappe.get_all("VL Room",
		filters=room_filters,
		fields=["name as room", "floor", "room_type", "room_status",
			"housekeeping_status as hk_status", "current_guest"],
		order_by="room_number asc")

	today = frappe.utils.today()
	for room in rooms:
		# Get today's HK task if any
		task = frappe.db.get_value("VL HK Task", {
			"room": room["room"],
			"scheduled_date": today,
			"status": ["not in", ["Cancelled"]]
		}, ["name", "assigned_to", "status"], as_dict=True)

		if task:
			room["hk_task"] = task.name
			room["assigned_to"] = task.assigned_to
			room["task_status"] = task.status
		else:
			room["hk_task"] = ""
			room["assigned_to"] = ""
			room["task_status"] = ""

	return rooms


def get_chart(data):
	if not data:
		return None

	status_counts = {}
	for d in data:
		s = d.get("hk_status") or "Unknown"
		status_counts[s] = status_counts.get(s, 0) + 1

	return {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [{"values": list(status_counts.values())}]
		},
		"type": "donut",
		"colors": ["#2ecc71", "#f39c12", "#e74c3c", "#95a5a6", "#3498db"],
	}
