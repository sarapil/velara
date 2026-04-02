# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Minibar Consumption — Room Minibar Usage Controller"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class VLMinibarConsumption(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname("VLMB-.YYYY.-.#####", doc=self)

	def validate(self):
		if not self.consumption_date:
			self.consumption_date = today()
		self.calculate_total()
		self.set_guest_from_room()

	def on_update(self):
		if not self.posted_to_folio and self.folio and flt(self.total_amount) > 0:
			self.post_to_folio()

	def calculate_total(self):
		total = 0
		for item in self.items or []:
			total += flt(item.amount)
		self.total_amount = flt(total, 2)

	def set_guest_from_room(self):
		if self.room and not self.guest:
			self.guest = frappe.db.get_value("VL Room", self.room, "current_guest")
			if not self.folio:
				self.folio = frappe.db.get_value("VL Room", self.room, "current_folio")

	def post_to_folio(self):
		if self.folio:
			from velara.utils import post_charge_to_folio
			post_charge_to_folio(
				self.folio, "Minibar", self.total_amount,
				_("Minibar consumption - Room {0}").format(self.room),
				"VL Minibar Consumption", self.name
			)
			self.db_set("posted_to_folio", 1)
