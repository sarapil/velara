// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL HK Task", {
	refresh(frm) {
		let colors = {
			"Pending": "orange", "Assigned": "blue", "In Progress": "yellow",
			"Completed": "green", "Inspected": "darkgrey", "Cancelled": "red"
		};
		frm.page.set_indicator(frm.doc.status, colors[frm.doc.status] || "grey");

		if (!frm.is_new()) {
			if (frm.doc.status === "Assigned" || frm.doc.status === "Pending") {
				frm.add_custom_button(__("Start Cleaning"), () => {
					frm.call("start_cleaning").then(() => frm.reload_doc());
				}).addClass("btn-primary");
			}
			if (frm.doc.status === "In Progress") {
				frm.add_custom_button(__("Complete"), () => {
					frm.call("complete_cleaning").then(() => frm.reload_doc());
				}).addClass("btn-primary");
			}
			if (frm.doc.status === "Completed") {
				frm.add_custom_button(__("Pass Inspection"), () => {
					frm.call("pass_inspection").then(() => frm.reload_doc());
				}).addClass("btn-success");
				frm.add_custom_button(__("Fail Inspection"), () => {
					let d = new frappe.ui.Dialog({
						title: __("Inspection Failed"),
						fields: [{ fieldname: "notes", fieldtype: "Text", label: __("Notes"), reqd: 1 }],
						primary_action(values) {
							frm.set_value("status", "In Progress");
							frm.set_value("inspection_notes", values.notes);
							frm.save().then(() => { d.hide(); });
						}
					});
					d.show();
				});
			}

			// Duration display
			if (frm.doc.duration_minutes) {
				frm.dashboard.add_indicator(
					__("Duration: {0} min", [frm.doc.duration_minutes]), "blue"
				);
			}
		}
	}
});
