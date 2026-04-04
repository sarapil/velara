# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VELARA — Customer Dashboard Override"""
import frappe
from frappe import _


def get_dashboard_data(data):
	"""Add VELARA links to Customer dashboard."""
	# Add transactions
	data.setdefault("transactions", [])

	data["transactions"].append({
		"label": _("Hotel"),
		"items": ["VL Reservation", "VL Folio", "VL Guest Feedback"]
	})

	# Add non-standard fieldnames for linking
	data.setdefault("non_standard_fieldnames", {})
	data["non_standard_fieldnames"]["VL Reservation"] = "customer"
	data["non_standard_fieldnames"]["VL Folio"] = "customer"
	data["non_standard_fieldnames"]["VL Guest Feedback"] = "customer"

	return data
