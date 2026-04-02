# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Night Audit — Nightly Audit Process Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, now_datetime


class VLNightAudit(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLNA-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.audit_date:
			self.audit_date = today()
		self.check_duplicate()

	def before_submit(self):
		self.run_audit()

	def check_duplicate(self):
		existing = frappe.db.get_value("VL Night Audit",
			{"audit_date": self.audit_date, "name": ["!=", self.name], "docstatus": 1})
		if existing:
			frappe.throw(_("Night audit already completed for {0}: {1}").format(
				self.audit_date, existing))

	def run_audit(self):
		"""Execute the full night audit process."""
		self.started_at = now_datetime()
		self.run_by = frappe.session.user
		self.status = "In Progress"

		# Statistics
		self.total_rooms = frappe.db.count("VL Room", {"room_status": ["!=", "Out of Service"]})
		self.occupied_rooms = frappe.db.count("VL Room", {"room_status": "Occupied"})
		self.occupancy_rate = flt(self.occupied_rooms / self.total_rooms * 100, 1) if self.total_rooms else 0

		# Revenue from today's folios
		revenue = frappe.db.sql("""
			SELECT
				COALESCE(SUM(total_charges), 0) as total,
				COALESCE(SUM(CASE WHEN folio_type='Guest' THEN total_charges ELSE 0 END), 0) as room_rev
			FROM `tabVL Folio`
			WHERE status = 'Open' AND docstatus < 2
		""", as_dict=True)[0]

		self.total_revenue = flt(revenue.total, 2)
		self.room_revenue = flt(revenue.room_rev, 2)
		self.fnb_revenue = 0
		self.other_revenue = flt(self.total_revenue - self.room_revenue, 2)

		# ADR & RevPAR
		self.adr = flt(self.room_revenue / self.occupied_rooms, 2) if self.occupied_rooms else 0
		self.revpar = flt(self.room_revenue / self.total_rooms, 2) if self.total_rooms else 0

		# Arrivals / Departures / No Shows
		self.arrivals = frappe.db.count("VL Check In",
			{"check_in_time": ["between", [self.audit_date, self.audit_date + " 23:59:59"]], "docstatus": 1})
		self.departures = frappe.db.count("VL Check Out",
			{"check_out_time": ["between", [self.audit_date, self.audit_date + " 23:59:59"]], "docstatus": 1})
		self.no_shows = frappe.db.count("VL Reservation",
			{"check_in_date": self.audit_date, "status": "No Show", "docstatus": 1})

		# Post room charges for in-house guests
		self.room_charges_posted = self._post_room_charges()

		self.status = "Completed"
		self.completed_at = now_datetime()

	def _post_room_charges(self):
		"""Post nightly room charges to all open folios."""
		count = 0
		open_folios = frappe.get_all("VL Folio",
			filters={"status": "Open", "docstatus": 0},
			fields=["name", "reservation", "room"])

		for folio in open_folios:
			if folio.reservation:
				rate = frappe.db.get_value("VL Reservation", folio.reservation, "room_rate")
				if flt(rate) > 0:
					try:
						from velara.utils import post_charge_to_folio
						post_charge_to_folio(folio.name, "Room Charge", rate,
							_("Nightly room charge - {0}").format(self.audit_date),
							"VL Night Audit", self.name)
						count += 1
					except Exception:
						frappe.log_error(f"Night Audit: Error posting charge for folio {folio.name}")

		return count
