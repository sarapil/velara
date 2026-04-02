"""
VELARA — Room API
"""
import frappe
from frappe import _
from frappe.utils import today


@frappe.whitelist()
def change_room_status(room, new_status, reason=None):
	"""Change a room's status with logging."""
	frappe.has_permission("VL Room", "write", throw=True)

	if not frappe.db.exists("VL Room", room):
		frappe.throw(_("Room {0} not found").format(room))

	old_status = frappe.db.get_value("VL Room", room, "status")
	frappe.db.set_value("VL Room", room, "status", new_status)

	# Log the change
	if frappe.db.exists("DocType", "VL Room Status Log"):
		log = frappe.new_doc("VL Room Status Log")
		log.room = room
		log.old_status = old_status
		log.new_status = new_status
		log.reason = reason
		log.changed_by = frappe.session.user
		log.insert(ignore_permissions=True)

	frappe.db.commit()
	return {"room": room, "old_status": old_status, "new_status": new_status}


@frappe.whitelist()
def get_floor_map(floor=None):
	"""Get room layout for floor map visualization."""
	frappe.has_permission("VL Room", "read", throw=True)

	filters = {"is_active": 1}
	if floor:
		filters["floor"] = floor

	rooms = frappe.get_all(
		"VL Room",
		filters=filters,
		fields=[
			"name", "room_number", "room_type", "floor", "wing",
			"status", "current_guest", "current_reservation",
			"hk_status", "bed_type", "is_smoking", "is_accessible",
			"is_connecting", "connecting_room"
		],
		order_by="floor asc, room_number asc"
	)

	# Get floors list
	floors = frappe.get_all(
		"VL Room",
		filters={"is_active": 1},
		fields=["distinct floor as floor"],
		order_by="floor asc"
	)

	return {
		"rooms": rooms,
		"floors": [f.floor for f in floors],
	}


@frappe.whitelist()
def bulk_status_update(rooms, new_status, reason=None):
	"""Update status for multiple rooms at once."""
	frappe.has_permission("VL Room", "write", throw=True)

	if isinstance(rooms, str):
		rooms = frappe.parse_json(rooms)

	updated = []
	for room in rooms:
		result = change_room_status(room, new_status, reason)
		updated.append(result)

	return updated
