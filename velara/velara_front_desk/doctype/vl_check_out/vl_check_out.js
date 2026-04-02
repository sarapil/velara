// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Check Out", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.page.set_indicator(__("Ready for Check-Out"), "orange");
			if (flt(frm.doc.folio_balance) > 0) {
				frm.dashboard.add_indicator(
					__("Outstanding Balance: {0}", [format_currency(frm.doc.folio_balance)]), "red"
				);
			}
		}
		if (frm.doc.docstatus === 1) {
			frm.page.set_indicator(__("Checked Out"), "green");
		}
	},

	reservation(frm) {
		if (frm.doc.reservation) {
			frappe.db.get_doc("VL Reservation", frm.doc.reservation).then(res => {
				frm.set_value("guest", res.guest);
				frm.set_value("guest_name", res.guest_name);
				frm.set_value("room", res.room);
				frm.set_value("folio", res.folio);
				if (res.folio) {
					frappe.db.get_value("VL Folio", res.folio, "balance").then(r => {
						frm.set_value("folio_balance", flt(r.message.balance));
					});
				}
			});
		}
	}
});
