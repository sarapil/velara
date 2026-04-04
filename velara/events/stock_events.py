# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VELARA — Stock Entry doc_events (Hotel inventory sync)"""
import frappe
from frappe import _


def on_validate(doc, method):
	"""Validate stock entries linked to hotel operations."""
	# Check if any item belongs to hotel item groups
	hotel_groups = ["Minibar", "Housekeeping Supplies", "F&B Supplies", "Guest Amenities"]
	for item in doc.items:
		item_group = frappe.db.get_value("Item", item.item_code, "item_group")
		if item_group in hotel_groups:
			doc.vl_hotel_stock = 1
			break


def on_submit(doc, method):
	"""When hotel-related stock entry is submitted, log for tracking."""
	if doc.get("vl_hotel_stock"):
		frappe.logger().info(
			f"VELARA: Hotel stock entry {doc.name} ({doc.stock_entry_type}) submitted"
		)
