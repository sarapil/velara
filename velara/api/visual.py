"""
VELARA — Visual Screen API
Provides data for frappe_visual graph components.
"""
import frappe
from frappe import _


@frappe.whitelist()
def get_guest_journey_graph(reservation=None):
	"""Get guest journey as a dependency graph for frappe.visual.dependencyGraph()."""
	nodes = [
		{"id": "search", "label": _("Search"), "type": "start", "status": "completed"},
		{"id": "reserve", "label": _("Reservation"), "type": "document", "status": "completed"},
		{"id": "confirm", "label": _("Confirmation"), "type": "action", "status": "completed"},
		{"id": "checkin", "label": _("Check-In"), "type": "action", "status": "active"},
		{"id": "stay", "label": _("In-House"), "type": "process", "status": "pending"},
		{"id": "charges", "label": _("Charges"), "type": "financial", "status": "pending"},
		{"id": "checkout", "label": _("Check-Out"), "type": "action", "status": "pending"},
		{"id": "invoice", "label": _("Invoice"), "type": "document", "status": "pending"},
		{"id": "payment", "label": _("Payment"), "type": "financial", "status": "pending"},
		{"id": "feedback", "label": _("Feedback"), "type": "end", "status": "pending"},
	]

	edges = [
		{"source": "search", "target": "reserve"},
		{"source": "reserve", "target": "confirm"},
		{"source": "confirm", "target": "checkin"},
		{"source": "checkin", "target": "stay"},
		{"source": "stay", "target": "charges"},
		{"source": "charges", "target": "checkout"},
		{"source": "checkout", "target": "invoice"},
		{"source": "invoice", "target": "payment"},
		{"source": "payment", "target": "feedback"},
	]

	if reservation and frappe.db.exists("VL Reservation", reservation):
		res = frappe.get_doc("VL Reservation", reservation)
		# Update node statuses based on reservation state
		status_map = {
			"Confirmed": {"search": "completed", "reserve": "completed", "confirm": "completed", "checkin": "active"},
			"Checked In": {"search": "completed", "reserve": "completed", "confirm": "completed",
						   "checkin": "completed", "stay": "active", "charges": "active"},
			"Checked Out": {"search": "completed", "reserve": "completed", "confirm": "completed",
						   "checkin": "completed", "stay": "completed", "charges": "completed",
						   "checkout": "completed", "invoice": "active"},
		}
		if res.status in status_map:
			for node in nodes:
				if node["id"] in status_map[res.status]:
					node["status"] = status_map[res.status][node["id"]]

	return {"nodes": nodes, "edges": edges}


@frappe.whitelist()
def get_hotel_module_map():
	"""Get VELARA module map for frappe.visual.appMap()."""
	modules = [
		{"id": "velara", "label": "VELARA", "type": "app", "icon": "building"},
		{"id": "front_desk", "label": _("Front Desk"), "type": "module", "icon": "bell-concierge"},
		{"id": "reservations", "label": _("Reservations"), "type": "module", "icon": "calendar-check"},
		{"id": "rooms", "label": _("Rooms"), "type": "module", "icon": "bed"},
		{"id": "housekeeping", "label": _("Housekeeping"), "type": "module", "icon": "spray-can"},
		{"id": "fnb", "label": _("F&B"), "type": "module", "icon": "utensils"},
		{"id": "revenue", "label": _("Revenue"), "type": "module", "icon": "chart-line"},
		{"id": "guest_services", "label": _("Guest Services"), "type": "module", "icon": "star"},
		{"id": "events", "label": _("Events"), "type": "module", "icon": "calendar-event"},
		{"id": "maintenance", "label": _("Maintenance"), "type": "module", "icon": "tool"},
		{"id": "loyalty", "label": _("Loyalty"), "type": "module", "icon": "heart"},
		{"id": "night_audit", "label": _("Night Audit"), "type": "module", "icon": "moon"},
		{"id": "spa", "label": _("Spa"), "type": "module", "icon": "leaf"},
		{"id": "reports", "label": _("Reports"), "type": "module", "icon": "chart-bar"},
	]

	edges = [{"source": "velara", "target": m["id"]} for m in modules if m["id"] != "velara"]

	return {"nodes": modules, "edges": edges}


@frappe.whitelist()
def get_reservation_workflow_graph():
	"""Get reservation workflow for frappe.visual.dependencyGraph()."""
	nodes = [
		{"id": "draft", "label": _("Draft"), "type": "state", "color": "#95a5a6"},
		{"id": "tentative", "label": _("Tentative"), "type": "state", "color": "#f39c12"},
		{"id": "confirmed", "label": _("Confirmed"), "type": "state", "color": "#3498db"},
		{"id": "guaranteed", "label": _("Guaranteed"), "type": "state", "color": "#2ecc71"},
		{"id": "checked_in", "label": _("Checked In"), "type": "state", "color": "#27ae60"},
		{"id": "checked_out", "label": _("Checked Out"), "type": "state", "color": "#8e44ad"},
		{"id": "cancelled", "label": _("Cancelled"), "type": "state", "color": "#e74c3c"},
		{"id": "no_show", "label": _("No Show"), "type": "state", "color": "#c0392b"},
	]

	edges = [
		{"source": "draft", "target": "tentative", "label": _("Submit")},
		{"source": "draft", "target": "confirmed", "label": _("Confirm")},
		{"source": "tentative", "target": "confirmed", "label": _("Confirm")},
		{"source": "tentative", "target": "cancelled", "label": _("Cancel")},
		{"source": "confirmed", "target": "guaranteed", "label": _("Guarantee")},
		{"source": "confirmed", "target": "checked_in", "label": _("Check In")},
		{"source": "confirmed", "target": "cancelled", "label": _("Cancel")},
		{"source": "confirmed", "target": "no_show", "label": _("No Show")},
		{"source": "guaranteed", "target": "checked_in", "label": _("Check In")},
		{"source": "guaranteed", "target": "cancelled", "label": _("Cancel")},
		{"source": "guaranteed", "target": "no_show", "label": _("No Show")},
		{"source": "checked_in", "target": "checked_out", "label": _("Check Out")},
	]

	return {"nodes": nodes, "edges": edges}
