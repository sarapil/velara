/**
 * VELARA — Sales Invoice DocType Extension
 * Shows folio link and hotel charge info
 */
frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		if (!frappe.boot.velara || !frappe.boot.velara.has_access) return;

		// Show linked folio
		if (frm.doc.vl_folio) {
			frm.add_custom_button(
				__("View Folio"),
				function () {
					frappe.set_route("Form", "VL Folio", frm.doc.vl_folio);
				},
				__("Velara")
			);
		}

		// Show room & reservation info
		if (frm.doc.vl_room) {
			frm.dashboard.add_indicator(
				__("Room: {0}", [frm.doc.vl_room]),
				"blue"
			);
		}
		if (frm.doc.vl_reservation) {
			frm.dashboard.add_indicator(
				__("Reservation: {0}", [frm.doc.vl_reservation]),
				"green"
			);
		}
	},
});
