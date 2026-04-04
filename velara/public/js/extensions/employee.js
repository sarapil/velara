// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * VELARA — Employee DocType Extension
 * Shows hotel department assignment
 */
frappe.ui.form.on("Employee", {
	refresh: function (frm) {
		if (!frappe.boot.velara || !frappe.boot.velara.has_access) return;

		if (frm.doc.vl_hotel_department) {
			frm.dashboard.add_indicator(
				__("Hotel Dept: {0}", [frm.doc.vl_hotel_department]),
				"blue"
			);
		}
	},
});
