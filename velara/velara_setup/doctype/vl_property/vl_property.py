# Copyright (c) 2026, ARKAN and contributors
# For license information, please see license.txt
"""VL Property — Hotel Property Controller"""

import frappe
from frappe import _
from frappe.model.document import Document


class VLProperty(Document):
	def validate(self):
		if not self.abbreviation and self.property_name:
			self.abbreviation = "".join(w[0].upper() for w in self.property_name.split()[:3])

	def get_room_summary(self):
		"""Get room counts by status for this property."""
		return frappe.get_all("VL Room",
			filters={"property": self.name},
			fields=["room_status as status", "count(*) as count"],
			group_by="room_status")
