"""VELARA — Employee doc_events"""
import frappe


def on_update(doc, method):
	"""Sync employee hotel department changes."""
	if not doc.get("vl_hotel_department"):
		return
	# Log department assignment for hotel staff tracking
	if doc.has_value_changed("vl_hotel_department"):
		frappe.logger().info(
			f"VELARA: Employee {doc.name} assigned to {doc.vl_hotel_department}"
		)
	# Sync property assignment
	if doc.has_value_changed("vl_property") and doc.get("vl_property"):
		frappe.logger().info(
			f"VELARA: Employee {doc.name} assigned to property {doc.vl_property}"
		)
