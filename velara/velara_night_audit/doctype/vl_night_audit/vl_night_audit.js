// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Night Audit", {
	refresh(frm) {
		let colors = { "In Progress": "orange", "Completed": "green", "Draft": "grey" };
		frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");

		if (frm.doc.docstatus === 1 && frm.doc.status === "Completed") {
			// Stats display
			frm.dashboard.add_indicator(__("Occupancy: {0}%", [frm.doc.occupancy_rate]), "blue");
			frm.dashboard.add_indicator(__("ADR: {0}", [format_currency(frm.doc.adr)]), "green");
			frm.dashboard.add_indicator(__("RevPAR: {0}", [format_currency(frm.doc.revpar)]), "green");
			frm.dashboard.add_indicator(__("Revenue: {0}", [format_currency(frm.doc.total_revenue)]), "blue");
		}
	}
});
