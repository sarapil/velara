# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""
VELARA — Notification Configuration
"""
import frappe


def get_notification_config():
	"""Return notification configuration for VELARA."""
	return {
		"for_doctype": {
			"VL Reservation": {"status": ["in", ["Confirmed", "Guaranteed"]]},
			"VL Service Request": {"status": ["in", ["Open", "Pending"]]},
			"VL HK Task": {"status": ["in", ["Pending", "Assigned"]]},
			"VL Maintenance Request": {"status": ["in", ["Open", "Assigned"]]},
			"VL Guest Feedback": {"status": "Pending Review"},
			"VL Folio": {"status": "Open"},
			"VL Event Booking": {"status": "Tentative"},
			"VL Spa Booking": {"status": "Confirmed"},
		},
		"for_module_doctypes": {
			"Velara Front Desk": ["VL Reservation", "VL Check In", "VL Folio"],
			"Velara Housekeeping": ["VL HK Task", "VL HK Inspection"],
			"Velara Guest Services": ["VL Service Request", "VL Concierge Task"],
			"Velara Maintenance": ["VL Maintenance Request"],
			"Velara Events": ["VL Event Booking"],
		},
	}
