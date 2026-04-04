// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.ui.form.on("VL Maintenance Request", {
	refresh(frm) {
		let colors = {
			"Open": "orange", "In Progress": "yellow", "Completed": "green",
			"On Hold": "blue", "Cancelled": "red"
		};
		frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");

		if (!frm.is_new()) {
			if (frm.doc.status === "Open") {
				frm.add_custom_button(__("Start Work"), () => {
					frm.call("start_work").then(() => frm.reload_doc());
				}).addClass("btn-primary");
			}
			if (frm.doc.status === "In Progress") {
				frm.add_custom_button(__("Complete"), () => {
					frm.call("complete_work").then(() => frm.reload_doc());
				}).addClass("btn-success");
			}
		}
	}
});
