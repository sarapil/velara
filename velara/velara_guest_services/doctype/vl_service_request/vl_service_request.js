// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Service Request", {
	refresh(frm) {
		let colors = {
			"Open": "orange", "In Progress": "yellow", "Completed": "green", "Cancelled": "red"
		};
		frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");

		if (!frm.is_new() && ["Open", "In Progress"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Resolve"), () => {
				frm.call("resolve").then(() => frm.reload_doc());
			}).addClass("btn-success");
		}
	}
});
