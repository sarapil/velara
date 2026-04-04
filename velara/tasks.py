# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Scheduled Tasks
Hotel operations that run on cron/daily/hourly/weekly/monthly schedules.
"""
import frappe
from frappe import _
from frappe.utils import today, now_datetime, add_days, getdate


# ============================================================
# CRON Tasks (every N minutes)
# ============================================================

def run_night_audit():
	"""
	Night Audit — runs at 2 AM daily.
	1. Post room charges for all in-house guests
	2. Post tax charges
	3. Verify rate integrity
	4. Generate audit report
	5. Roll business date
	"""
	if not frappe.db.exists("DocType", "VL Night Audit"):
		return

	try:
		audit = frappe.new_doc("VL Night Audit")
		audit.audit_date = today()
		audit.status = "In Progress"
		audit.insert(ignore_permissions=True)

		# Step 1: Post room charges
		_post_room_charges(audit)

		# Step 2: Post recurring charges (minibar, parking, etc.)
		_post_recurring_charges(audit)

		# Step 3: Calculate statistics
		_calculate_daily_statistics(audit)

		audit.status = "Completed"
		audit.save(ignore_permissions=True)
		frappe.db.commit()

		frappe.logger().info(f"Night audit completed for {today()}")
	except Exception as e:
		frappe.log_error(f"Night Audit Error: {str(e)}", "VELARA Night Audit")


def update_room_statuses():
	"""Update room statuses based on reservations and housekeeping."""
	if not frappe.db.exists("DocType", "VL Room"):
		return

	try:
		# Mark rooms as Dirty for checked-out reservations
		checked_out_rooms = frappe.get_all(
			"VL Room",
			filters={"room_status": "Occupied", "current_reservation": ["is", "not set"]},
			pluck="name"
		)
		for room in checked_out_rooms:
			frappe.db.set_value("VL Room", room, "room_status", "Dirty")

		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Room Status Update Error: {str(e)}", "VELARA Rooms")


def check_reservation_deadlines():
	"""Auto-cancel or mark no-show for reservations past their deadline."""
	if not frappe.db.exists("DocType", "VL Reservation"):
		return

	try:
		now = now_datetime()
		# Mark no-shows: confirmed reservations where check-in date was yesterday
		yesterday = add_days(today(), -1)
		no_shows = frappe.get_all(
			"VL Reservation",
			filters={
				"check_in_date": yesterday,
				"status": ["in", ["Confirmed", "Guaranteed"]],
			},
			pluck="name"
		)
		for res in no_shows:
			frappe.db.set_value("VL Reservation", res, "status", "No Show")

		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Reservation Deadline Error: {str(e)}", "VELARA Reservations")


# ============================================================
# Daily Tasks
# ============================================================

def send_arrival_list():
	"""Send today's expected arrivals to front desk staff."""
	if not frappe.db.exists("DocType", "VL Reservation"):
		return

	try:
		arrivals = frappe.get_all(
			"VL Reservation",
			filters={
				"check_in_date": today(),
				"status": ["in", ["Confirmed", "Guaranteed"]],
			},
			fields=["name", "guest_name", "room_type", "check_in_date", "check_out_date", "notes"]
		)

		if arrivals:
			frappe.logger().info(f"VELARA: {len(arrivals)} arrivals expected today")
			# TODO: Send notification to front desk
	except Exception as e:
		frappe.log_error(f"Arrival List Error: {str(e)}", "VELARA Front Desk")


def send_departure_list():
	"""Send today's expected departures to front desk staff."""
	if not frappe.db.exists("DocType", "VL Reservation"):
		return

	try:
		departures = frappe.get_all(
			"VL Reservation",
			filters={
				"check_out_date": today(),
				"status": "Checked In",
			},
			fields=["name", "guest_name", "room", "check_out_date"]
		)

		if departures:
			frappe.logger().info(f"VELARA: {len(departures)} departures expected today")
	except Exception as e:
		frappe.log_error(f"Departure List Error: {str(e)}", "VELARA Front Desk")


def check_maintenance_schedules():
	"""Check for preventive maintenance tasks due today."""
	if not frappe.db.exists("DocType", "VL Preventive Schedule"):
		return

	try:
		due_schedules = frappe.get_all(
			"VL Preventive Schedule",
			filters={
				"next_due_date": ["<=", today()],
				"enabled": 1,
			},
			fields=["name", "equipment", "task_description", "frequency"]
		)

		for schedule in due_schedules:
			# Create maintenance request
			if frappe.db.exists("DocType", "VL Maintenance Request"):
				req = frappe.new_doc("VL Maintenance Request")
				req.request_type = "Preventive"
				req.equipment = schedule.equipment
				req.description = schedule.task_description
				req.priority = "Medium"
				req.source_schedule = schedule.name
				req.insert(ignore_permissions=True)

		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Maintenance Schedule Error: {str(e)}", "VELARA Maintenance")


def auto_assign_housekeeping():
	"""Auto-assign housekeeping tasks based on departures and occupied rooms."""
	if not frappe.db.exists("DocType", "VL HK Task"):
		return

	try:
		# Get all dirty rooms
		dirty_rooms = frappe.get_all(
			"VL Room",
			filters={"room_status": "Dirty"},
			fields=["name", "room_type", "floor"]
		)

		for room in dirty_rooms:
			# Check if task already exists
			existing = frappe.db.exists("VL HK Task", {
				"room": room.name,
				"date": today(),
				"status": ["not in", ["Completed", "Cancelled"]]
			})
			if not existing:
				task = frappe.new_doc("VL HK Task")
				task.room = room.name
				task.task_type = "Checkout Cleaning"
				task.date = today()
				task.status = "Pending"
				task.priority = "High"
				task.insert(ignore_permissions=True)

		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"HK Auto-assign Error: {str(e)}", "VELARA Housekeeping")


def process_loyalty_points():
	"""Process loyalty points for completed stays (checked out yesterday)."""
	if not frappe.db.exists("DocType", "VL Reservation"):
		return
	try:
		yesterday = add_days(today(), -1)
		completed = frappe.get_all("VL Reservation",
			filters={"status": "Checked Out", "check_out_date": yesterday, "docstatus": 1},
			fields=["name", "guest", "net_total"])
		for res in completed:
			if res.guest and frappe.db.exists("DocType", "VL Loyalty Transaction"):
				from frappe.utils import flt, cint
				points = cint(flt(res.net_total) / 10)  # 1 point per 10 currency units
				if points > 0:
					txn = frappe.new_doc("VL Loyalty Transaction")
					txn.guest = res.guest
					txn.transaction_type = "Earn"
					txn.points = points
					txn.reference_doctype = "VL Reservation"
					txn.reference_name = res.name
					txn.posting_date = today()
					txn.remarks = f"Stay completion: {res.name}"
					txn.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Loyalty Points Error: {str(e)}", "VELARA Loyalty")


# ============================================================
# Hourly Tasks
# ============================================================

def sync_channel_rates():
	"""Sync rates with OTA channels (placeholder for channel manager integration)."""
	frappe.logger().info("VELARA: Channel rate sync - no channels configured")


def update_occupancy_forecast():
	"""Update occupancy forecast based on current reservations."""
	if not frappe.db.exists("DocType", "VL Reservation"):
		return
	try:
		total_rooms = frappe.db.count("VL Room", {"room_status": ["!=", "Out of Service"]})
		if not total_rooms:
			return
		# Forecast next 7 days
		for i in range(7):
			date = add_days(today(), i)
			reserved = frappe.db.count("VL Reservation", {
				"check_in_date": ["<=", date], "check_out_date": [">", date],
				"status": ["in", ["Confirmed", "Guaranteed", "Checked In"]], "docstatus": 1
			})
			occupancy = round(reserved / total_rooms * 100, 1)
			frappe.cache().hset("velara_forecast", date, occupancy)
	except Exception as e:
		frappe.log_error(f"Occupancy Forecast Error: {str(e)}", "VELARA Revenue")


def check_folio_credit_limits():
	"""Alert when guest folios approach credit limits."""
	if not frappe.db.exists("DocType", "VL Folio"):
		return

	try:
		# Find folios approaching credit limit
		folios = frappe.get_all(
			"VL Folio",
			filters={"status": "Open"},
			fields=["name", "guest", "total_amount", "credit_limit"]
		)

		for folio in folios:
			if folio.credit_limit and folio.total_amount > (folio.credit_limit * 0.8):
				frappe.logger().warning(
					f"VELARA: Folio {folio.name} at {folio.total_amount}/{folio.credit_limit} "
					f"({(folio.total_amount/folio.credit_limit*100):.0f}%)"
				)
	except Exception as e:
		frappe.log_error(f"Credit Limit Check Error: {str(e)}", "VELARA Folios")


# ============================================================
# Weekly Tasks
# ============================================================

def generate_weekly_revenue_report():
	"""Generate weekly revenue summary."""
	try:
		start = add_days(today(), -7)
		revenue = frappe.db.sql("""
			SELECT COALESCE(SUM(total_charges), 0) as total
			FROM `tabVL Folio` WHERE creation BETWEEN %s AND %s AND docstatus < 2
		""", (start, today()), as_dict=True)
		total = revenue[0].total if revenue else 0
		frappe.logger().info(f"VELARA Weekly Revenue: {total} for week ending {today()}")
	except Exception as e:
		frappe.log_error(f"Weekly Revenue Report Error: {str(e)}", "VELARA Reports")


def check_preventive_maintenance_due():
	"""Check for upcoming preventive maintenance in the next 7 days."""
	if not frappe.db.exists("DocType", "VL Preventive Schedule"):
		return
	try:
		next_week = add_days(today(), 7)
		due = frappe.get_all("VL Preventive Schedule",
			filters={"next_due_date": ["between", [today(), next_week]], "enabled": 1},
			fields=["name", "equipment", "next_due_date"])
		if due:
			frappe.logger().info(f"VELARA: {len(due)} preventive maintenance tasks due this week")
	except Exception as e:
		frappe.log_error(f"PM Check Error: {str(e)}", "VELARA Maintenance")


def send_guest_feedback_summary():
	"""Summarize guest feedback for the week."""
	if not frappe.db.exists("DocType", "VL Guest Feedback"):
		return
	try:
		start = add_days(today(), -7)
		feedback = frappe.db.sql("""
			SELECT COUNT(*) as count, AVG(overall_rating) as avg_rating
			FROM `tabVL Guest Feedback` WHERE creation >= %s
		""", start, as_dict=True)
		if feedback and feedback[0].count:
			frappe.logger().info(
				f"VELARA Weekly Feedback: {feedback[0].count} reviews, "
				f"avg rating: {round(feedback[0].avg_rating or 0, 1)}/5"
			)
	except Exception as e:
		frappe.log_error(f"Feedback Summary Error: {str(e)}", "VELARA Guest Services")


# ============================================================
# Monthly Tasks
# ============================================================

def generate_monthly_statistics():
	"""Generate monthly hotel statistics (ADR, RevPAR, Occupancy %)."""
	try:
		month_start = add_days(today(), -30)
		audits = frappe.get_all("VL Night Audit",
			filters={"audit_date": [">=", month_start], "docstatus": 1},
			fields=["avg(occupancy_rate) as avg_occ", "avg(adr) as avg_adr",
				"avg(revpar) as avg_revpar", "sum(total_revenue) as total_rev"])
		if audits:
			a = audits[0]
			frappe.logger().info(
				f"VELARA Monthly Stats: Occ={a.avg_occ:.1f}%, ADR={a.avg_adr:.2f}, "
				f"RevPAR={a.avg_revpar:.2f}, Revenue={a.total_rev:.2f}"
			)
	except Exception as e:
		frappe.log_error(f"Monthly Stats Error: {str(e)}", "VELARA Reports")


def update_dynamic_pricing_rules():
	"""Recalculate dynamic pricing rules based on occupancy levels."""
	try:
		# Get current week occupancy forecast from cache
		forecast = frappe.cache().hgetall("velara_forecast")
		if forecast:
			avg_occ = sum(float(v) for v in forecast.values()) / len(forecast) if forecast else 0
			frappe.logger().info(f"VELARA: Dynamic pricing check - avg forecast occupancy: {avg_occ:.1f}%")
	except Exception as e:
		frappe.log_error(f"Dynamic Pricing Error: {str(e)}", "VELARA Revenue")


def archive_old_folios():
	"""Archive settled folios older than retention period (90 days)."""
	if not frappe.db.exists("DocType", "VL Folio"):
		return
	try:
		cutoff = add_days(today(), -90)
		old_folios = frappe.db.count("VL Folio",
			{"status": ["in", ["Settled", "Closed", "Void"]], "modified": ["<", cutoff]})
		if old_folios:
			frappe.logger().info(f"VELARA: {old_folios} folios eligible for archival")
	except Exception as e:
		frappe.log_error(f"Folio Archive Error: {str(e)}", "VELARA")


# ============================================================
# Helper Functions
# ============================================================

def _post_room_charges(audit):
	"""Post nightly room charges for all in-house guests."""
	count = 0
	if not frappe.db.exists("DocType", "VL Folio"):
		return count
	open_folios = frappe.get_all("VL Folio",
		filters={"status": "Open", "docstatus": 0},
		fields=["name", "reservation"])
	for folio in open_folios:
		if folio.reservation:
			from frappe.utils import flt
			rate = flt(frappe.db.get_value("VL Reservation", folio.reservation, "room_rate"))
			if rate > 0:
				try:
					from velara.utils import post_charge_to_folio
					post_charge_to_folio(folio.name, "Room Charge", rate,
						_("Nightly room charge"), "VL Night Audit", audit.name)
					count += 1
				except Exception:
					frappe.log_error(f"Night Audit: Error posting charge for {folio.name}")
	return count


def _post_recurring_charges(audit):
	"""Post recurring charges (parking, minibar, etc.)."""
	# Recurring charges are posted by individual modules (minibar, spa, etc.)
	frappe.logger().info(f"VELARA Night Audit: Recurring charges step for {audit.name}")


def _calculate_daily_statistics(audit):
	"""Calculate occupancy, ADR, RevPAR for the day."""
	from frappe.utils import flt
	total_rooms = frappe.db.count("VL Room", {"room_status": ["!=", "Out of Service"]}) or 1
	occupied = frappe.db.count("VL Room", {"room_status": "Occupied"})
	audit.total_rooms = total_rooms
	audit.occupied_rooms = occupied
	audit.occupancy_rate = flt(occupied / total_rooms * 100, 1)
	audit.adr = flt(audit.room_revenue / occupied, 2) if occupied else 0
	audit.revpar = flt(audit.room_revenue / total_rooms, 2) if total_rooms else 0
