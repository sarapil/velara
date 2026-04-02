"""
VELARA — Reservation API
"""
import frappe
from frappe import _
from frappe.utils import today, getdate, flt
from velara.utils import check_room_availability, calculate_room_rate


@frappe.whitelist()
def check_availability(room_type, check_in, check_out):
	"""Check room availability for a date range."""
	available_rooms = check_room_availability(room_type, check_in, check_out)
	return {
		"available": len(available_rooms),
		"rooms": available_rooms,
	}


@frappe.whitelist()
def get_rate_quote(room_type, check_in, check_out, rate_plan=None, guest=None):
	"""Get a rate quote for a stay."""
	total = calculate_room_rate(room_type, check_in, check_out, rate_plan, guest)
	from frappe.utils import date_diff
	nights = date_diff(check_out, check_in)

	return {
		"total": flt(total, 2),
		"nights": nights,
		"avg_nightly_rate": flt(total / nights, 2) if nights > 0 else 0,
		"room_type": room_type,
		"rate_plan": rate_plan,
	}


@frappe.whitelist()
def quick_reservation(guest, room_type, check_in, check_out, rate_plan=None, room=None, notes=None):
	"""Create a reservation quickly from the front desk."""
	frappe.has_permission("VL Reservation", "create", throw=True)

	if not frappe.db.exists("DocType", "VL Reservation"):
		frappe.throw(_("VL Reservation DocType not found"))

	# Validate availability
	available = check_room_availability(room_type, check_in, check_out)
	if not available:
		frappe.throw(_("No rooms available for {0} from {1} to {2}").format(
			room_type, check_in, check_out
		))

	# Auto-assign room if not specified
	if not room and available:
		room = available[0]

	# Calculate rate
	total = calculate_room_rate(room_type, check_in, check_out, rate_plan, guest)

	reservation = frappe.new_doc("VL Reservation")
	reservation.guest = guest
	reservation.room_type = room_type
	reservation.room = room
	reservation.check_in_date = check_in
	reservation.check_out_date = check_out
	reservation.rate_plan = rate_plan
	reservation.total_amount = total
	reservation.notes = notes
	reservation.status = "Confirmed"
	reservation.source = "Front Desk"
	reservation.insert()

	return reservation.as_dict()
