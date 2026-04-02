// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Check In", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.page.set_indicator(__("Ready for Check-In"), "blue");
		}
		if (frm.doc.docstatus === 1) {
			frm.page.set_indicator(__("Checked In"), "green");
			frm.dashboard.add_indicator(__("Room: {0}", [frm.doc.room]), "green");
		}
	},

	reservation(frm) {
		if (frm.doc.reservation) {
			frappe.db.get_doc("VL Reservation", frm.doc.reservation).then(res => {
				frm.set_value("guest", res.guest);
				frm.set_value("guest_name", res.guest_name);
				frm.set_value("room", res.room);
			});
		}
	}
});
