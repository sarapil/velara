# Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
# Developer Website: https://arkan.it.com
# License: MIT
# For license information, please see license.txt

"""VL Guest — Guest Profile Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VLGuest(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLG-.YYYY.-.#####", doc=self)

	def validate(self):
		self.set_guest_name()
		self.validate_email()
		self.validate_id()

	def after_insert(self):
		self.link_to_customer()

	def set_guest_name(self):
		parts = [self.first_name or "", self.last_name or ""]
		self.guest_name = " ".join(p for p in parts if p).strip()
		if not self.guest_name:
			frappe.throw(_("First Name or Last Name is required"))

	def validate_email(self):
		if self.email and not frappe.utils.validate_email_address(self.email, throw=False):
			frappe.throw(_("Invalid email address: {0}").format(self.email))

	def validate_id(self):
		if self.id_number and self.id_type:
			existing = frappe.db.get_value("VL Guest",
				{"id_type": self.id_type, "id_number": self.id_number, "name": ["!=", self.name]},
				"name")
			if existing:
				frappe.throw(_("A guest with {0} number {1} already exists: {2}").format(
					self.id_type, self.id_number, existing))

	def link_to_customer(self):
		"""Auto-create a Customer record for this guest."""
		if not self.customer and self.guest_name:
			try:
				customer = frappe.new_doc("Customer")
				customer.customer_name = self.guest_name
				customer.customer_type = "Individual"
				customer.customer_group = frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups"
				customer.territory = frappe.db.get_single_value("Selling Settings", "territory") or "All Territories"
				customer.vl_guest = self.name
				customer.insert(ignore_permissions=True)
				self.db_set("customer", customer.name)
			except Exception:
				frappe.log_error("VELARA: Error creating Customer for guest")

	def get_stay_history(self):
		"""Get reservation history for this guest."""
		return frappe.get_all("VL Reservation",
			filters={"guest": self.name, "docstatus": 1},
			fields=["name", "check_in_date", "check_out_date", "room", "room_type", "status", "net_total"],
			order_by="check_in_date desc")
