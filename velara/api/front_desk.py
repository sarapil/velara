# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Front Desk API
Provides data for the Front Desk operations page.
"""
import frappe
from frappe import _
from frappe.utils import today, getdate, flt, add_days, date_diff


@frappe.whitelist()
def get_front_desk_data():
	"""Get all front desk operational data in a single call."""
	frappe.has_permission("VL Reservation", "read", throw=True)

	data = {
		"arrivals_count": 0,
		"departures_count": 0,
		"in_house_count": 0,
		"available_rooms": 0,
		"pending_arrivals": [],
		"pending_departures": [],
		"in_house": [],
	}

	# Available rooms count
	if frappe.db.exists("DocType", "VL Room"):
		data["available_rooms"] = frappe.db.count(
			"VL Room", {"room_status": "Available", "is_active": 1}
		)

	if not frappe.db.exists("DocType", "VL Reservation"):
		return data

	# Pending arrivals (today, not yet checked in)
	data["pending_arrivals"] = frappe.get_all(
		"VL Reservation",
		filters={
			"check_in_date": today(),
			"status": "Confirmed",
		},
		fields=[
			"name", "guest", "guest_name", "room_type", "room",
			"check_in_date", "check_out_date", "adults", "children",
			"rate_plan", "booking_source", "special_requests",
		],
		order_by="guest_name asc",
	)
	data["arrivals_count"] = len(data["pending_arrivals"])

	# Pending departures (today, still checked in)
	data["pending_departures"] = frappe.get_all(
		"VL Reservation",
		filters={
			"check_out_date": today(),
			"status": "Checked In",
		},
		fields=[
			"name", "guest", "guest_name", "room",
			"check_out_date", "folio", "balance",
		],
		order_by="guest_name asc",
	)
	data["departures_count"] = len(data["pending_departures"])

	# In-house guests
	in_house = frappe.get_all(
		"VL Reservation",
		filters={"status": "Checked In"},
		fields=[
			"name", "guest", "guest_name", "room", "room_type",
			"check_in_date", "check_out_date", "folio",
		],
		order_by="room asc",
	)

	for r in in_house:
		r["nights"] = date_diff(r.get("check_out_date"), r.get("check_in_date")) or 0

	data["in_house"] = in_house
	data["in_house_count"] = len(in_house)

	return data


@frappe.whitelist()
def walk_in_check_in(first_name, room_type, nights=1, last_name=None,
                     mobile=None, email=None, id_type=None, id_number=None):
	"""Create a guest and reservation for a walk-in, then return the reservation name."""
	frappe.has_permission("VL Reservation", "create", throw=True)

	nights = int(nights) or 1
	check_in = today()
	check_out = add_days(check_in, nights)

	# ---- Create or find guest ----
	guest = None
	if mobile:
		guest = frappe.db.get_value("VL Guest", {"mobile": mobile})
	if not guest and email:
		guest = frappe.db.get_value("VL Guest", {"email": email})

	if not guest:
		guest_doc = frappe.new_doc("VL Guest")
		guest_doc.first_name = first_name
		guest_doc.last_name = last_name or ""
		guest_doc.mobile = mobile
		guest_doc.email = email
		if id_type:
			guest_doc.id_type = id_type
		if id_number:
			guest_doc.id_number = id_number
		guest_doc.insert()
		guest = guest_doc.name

	# ---- Find available room ----
	from velara.utils import check_room_availability, calculate_room_rate

	available_rooms = check_room_availability(room_type, check_in, check_out)
	if not available_rooms:
		frappe.throw(
			_("No {0} rooms available for the selected dates").format(room_type)
		)

	room = available_rooms[0]
	total = calculate_room_rate(room_type, check_in, check_out)

	# ---- Create reservation ----
	reservation = frappe.new_doc("VL Reservation")
	reservation.guest = guest
	reservation.room_type = room_type
	reservation.room = room
	reservation.check_in_date = check_in
	reservation.check_out_date = check_out
	reservation.net_total = total
	reservation.status = "Confirmed"
	reservation.booking_source = "Walk-In"
	reservation.insert()

	return reservation.name


@frappe.whitelist()
def search_guest(query):
	"""Proxy to guest.search_guest for convenience from front desk page."""
	frappe.only_for(["VL User", "VL Manager", "System Manager"])

	from velara.api.guest import search_guest as _search_guest

	return _search_guest(query)
