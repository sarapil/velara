// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Room", {
	refresh(frm) {
		// Status badges
		let colors = {
			"Available": "green", "Occupied": "red", "Reserved": "blue",
			"Dirty": "orange", "Clean": "green", "Inspected": "darkgrey",
			"Out of Order": "red", "Out of Service": "grey"
		};
		frm.page.set_indicator(frm.doc.room_status, colors[frm.doc.room_status] || "grey");

		// Quick status change buttons
		if (!frm.is_new()) {
			if (frm.doc.room_status === "Dirty") {
				frm.add_custom_button(__("Mark Clean"), () => {
					frm.call("change_status", { new_status: "Clean" }).then(() => frm.reload_doc());
				});
			}
			if (frm.doc.room_status === "Clean") {
				frm.add_custom_button(__("Mark Inspected"), () => {
					frm.call("change_status", { new_status: "Inspected" }).then(() => frm.reload_doc());
				});
			}
			if (!["Out of Order", "Out of Service"].includes(frm.doc.room_status)) {
				frm.add_custom_button(__("Block Room"), () => {
					frappe.new_doc("VL Room Block", { room: frm.doc.name });
				}, __("Actions"));
			}
			if (["Inspected", "Clean"].includes(frm.doc.room_status)) {
				frm.add_custom_button(__("Mark Available"), () => {
					frm.call("change_status", { new_status: "Available" }).then(() => frm.reload_doc());
				});
			}
		}

		// Current guest info
		if (frm.doc.current_guest) {
			frm.dashboard.add_indicator(__("Guest: {0}", [frm.doc.current_guest]), "blue");
		}
		if (frm.doc.current_reservation) {
			frm.dashboard.add_indicator(__("Res: {0}", [frm.doc.current_reservation]), "green");
		}
	}
});
