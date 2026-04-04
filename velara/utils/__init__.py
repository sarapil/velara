# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Utility Functions & Jinja Helpers
"""
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, today, date_diff, formatdate


# ============================================================
# Jinja Template Methods
# ============================================================

jinja_methods = [
	"velara.utils.get_room_status_color",
	"velara.utils.format_stay_duration",
	"velara.utils.get_occupancy_percentage",
	"velara.utils.format_currency_hotel",
]


def get_room_status_color(status):
	"""Return color code for room status — used in templates and visual screens."""
	colors = {
		"Available": "#2ecc71",      # Green
		"Occupied": "#e74c3c",       # Red
		"Reserved": "#3498db",       # Blue
		"Dirty": "#f39c12",          # Orange
		"Clean": "#2ecc71",          # Green
		"Inspected": "#27ae60",      # Dark Green
		"Out of Order": "#95a5a6",   # Gray
		"Out of Service": "#7f8c8d", # Dark Gray
		"Due Out": "#e67e22",        # Dark Orange
		"Due In": "#9b59b6",         # Purple
	}
	return colors.get(status, "#bdc3c7")


def format_stay_duration(check_in, check_out):
	"""Format stay duration for display."""
	if not check_in or not check_out:
		return ""

	days = date_diff(check_out, check_in)
	if days == 1:
		return _("1 Night")
	return _("{0} Nights").format(days)


def get_occupancy_percentage(occupied=None, total=None):
	"""Calculate occupancy percentage."""
	if occupied is None or total is None:
		try:
			total = frappe.db.count("VL Room", {"is_active": 1})
			occupied = frappe.db.count("VL Room", {"status": "Occupied"})
		except Exception:
			return 0

	if not total:
		return 0
	return flt(occupied / total * 100, 1)


def format_currency_hotel(amount, currency=None):
	"""Format currency with hotel conventions."""
	if not currency:
		currency = frappe.defaults.get_global_default("currency") or "USD"
	return frappe.format_value(amount, {"fieldtype": "Currency", "options": "currency"})


# ============================================================
# Room Availability Engine
# ============================================================

def check_room_availability(room_type, check_in, check_out, exclude_reservation=None):
	"""
	Check room availability for a given room type and date range.
	Returns list of available rooms.
	"""
	if not frappe.db.exists("DocType", "VL Room"):
		return []

	check_in = getdate(check_in)
	check_out = getdate(check_out)

	# Get all rooms of this type
	all_rooms = frappe.get_all(
		"VL Room",
		filters={
			"room_type": room_type,
			"is_active": 1,
			"status": ["not in", ["Out of Order", "Out of Service"]],
		},
		pluck="name"
	)

	if not all_rooms:
		return []

	# Get rooms that have overlapping reservations
	filters = {
		"room": ["in", all_rooms],
		"status": ["not in", ["Cancelled", "No Show", "Checked Out"]],
		"check_in_date": ["<", check_out],
		"check_out_date": [">", check_in],
	}

	if exclude_reservation:
		filters["name"] = ["!=", exclude_reservation]

	occupied_rooms = frappe.get_all(
		"VL Reservation",
		filters=filters,
		pluck="room"
	)

	# Return rooms not in the occupied list
	available = [r for r in all_rooms if r not in occupied_rooms]
	return available


def get_room_count_by_status():
	"""Get room counts grouped by status."""
	if not frappe.db.exists("DocType", "VL Room"):
		return {}

	rooms = frappe.get_all(
		"VL Room",
		filters={"is_active": 1},
		fields=["status", "count(*) as count"],
		group_by="status"
	)
	return {r.status: r.count for r in rooms}


# ============================================================
# Rate Calculation Engine
# ============================================================

def calculate_room_rate(room_type, check_in, check_out, rate_plan=None, guest=None):
	"""
	Calculate room rate for a stay.
	Considers: base rate, season, day of week, occupancy, loyalty discount.
	"""
	check_in = getdate(check_in)
	check_out = getdate(check_out)
	nights = date_diff(check_out, check_in)

	if nights <= 0:
		return 0

	# Get base rate
	base_rate = _get_base_rate(room_type, rate_plan)

	total = 0
	current_date = check_in
	for i in range(nights):
		nightly_rate = base_rate

		# Apply season adjustment
		nightly_rate = _apply_season_rate(nightly_rate, current_date)

		# Apply day-of-week adjustment (weekend premium)
		if current_date.weekday() in [4, 5]:  # Friday, Saturday
			nightly_rate *= 1.1  # 10% weekend premium

		total += nightly_rate
		current_date = getdate(add_days_to_date(current_date, 1))

	# Apply loyalty discount
	if guest:
		total = _apply_loyalty_discount(total, guest)

	return flt(total, 2)


def _get_base_rate(room_type, rate_plan=None):
	"""Get base rate for room type from rate plan."""
	if rate_plan and frappe.db.exists("DocType", "VL Rate Plan"):
		rate = frappe.db.get_value("VL Rate Plan", rate_plan, "base_rate")
		if rate:
			return flt(rate)

	if frappe.db.exists("DocType", "VL Room Type"):
		rate = frappe.db.get_value("VL Room Type", room_type, "default_rate")
		if rate:
			return flt(rate)

	return 0


def _apply_season_rate(rate, date):
	"""Apply seasonal rate adjustment."""
	if not frappe.db.exists("DocType", "VL Season"):
		return rate

	season = frappe.db.get_value(
		"VL Season",
		{"start_date": ["<=", date], "end_date": [">=", date], "is_active": 1},
		"rate_multiplier"
	)

	if season:
		return rate * flt(season)
	return rate


def _apply_loyalty_discount(total, guest):
	"""Apply loyalty tier discount."""
	if not frappe.db.exists("DocType", "VL Loyalty Tier"):
		return total

	tier = frappe.db.get_value("VL Guest", guest, "loyalty_tier")
	if tier:
		discount = frappe.db.get_value("VL Loyalty Tier", tier, "discount_percent")
		if discount:
			total *= (1 - flt(discount) / 100)

	return total


def add_days_to_date(date, days):
	"""Add days to a date."""
	from frappe.utils import add_days
	return add_days(date, days)


# ============================================================
# Folio Management
# ============================================================

def post_charge_to_folio(folio, charge_type, amount, description=None, reference_type=None, reference_name=None):
	"""Post a charge to guest folio."""
	if not frappe.db.exists("DocType", "VL Folio Charge"):
		return None

	charge = frappe.new_doc("VL Folio Charge")
	charge.folio = folio
	charge.charge_type = charge_type
	charge.amount = flt(amount)
	charge.description = description or charge_type
	charge.posting_date = today()
	charge.posting_time = frappe.utils.now_datetime().strftime("%H:%M:%S")
	charge.reference_type = reference_type
	charge.reference_name = reference_name
	charge.insert(ignore_permissions=True)

	# Update folio total
	_update_folio_totals(folio)

	return charge.name


def _update_folio_totals(folio):
	"""Recalculate folio totals."""
	if not frappe.db.exists("DocType", "VL Folio"):
		return

	charges = frappe.get_all(
		"VL Folio Charge",
		filters={"folio": folio, "status": ["!=", "Void"]},
		fields=["sum(amount) as total_charges", "sum(payment_amount) as total_payments"]
	)

	if charges:
		total_charges = flt(charges[0].total_charges)
		total_payments = flt(charges[0].total_payments)
		balance = total_charges - total_payments

		frappe.db.set_value("VL Folio", folio, {
			"total_amount": total_charges,
			"paid_amount": total_payments,
			"balance": balance,
		})
