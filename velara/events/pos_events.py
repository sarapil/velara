"""VELARA — POS Invoice doc_events (Hotel POS → Folio posting)"""
import frappe
from frappe import _
from frappe.utils import flt


def on_submit(doc, method):
	"""When a POS Invoice is submitted, check for Post-to-Room charges."""
	# Check if payment mode includes "Post to Room" / "Room Charge"
	for payment in doc.get("payments", []):
		if payment.mode_of_payment and "room" in payment.mode_of_payment.lower():
			_post_to_guest_folio(doc, payment)


def _post_to_guest_folio(doc, payment):
	"""Post POS charge to guest folio (Post-to-Room feature)."""
	if not frappe.db.exists("DocType", "VL Folio Charge"):
		return

	# The POS Invoice should reference a room or guest
	room = doc.get("vl_room")
	if not room:
		return

	# Find the active folio for this room
	folio = frappe.db.get_value(
		"VL Folio",
		{"room": room, "status": "Open"},
		"name"
	)

	if not folio:
		frappe.logger().warning(f"VELARA: No open folio for room {room} — POS charge not posted")
		return

	try:
		from velara.utils import post_charge_to_folio
		charge_type = "F&B" if doc.get("selling_price_list") else "Miscellaneous"
		post_charge_to_folio(
			folio=folio,
			charge_type=charge_type,
			amount=flt(payment.amount),
			description=f"POS: {doc.name}",
			reference_type="POS Invoice",
			reference_name=doc.name
		)
	except Exception as e:
		frappe.log_error(f"VELARA POS Post Error: {str(e)}")
