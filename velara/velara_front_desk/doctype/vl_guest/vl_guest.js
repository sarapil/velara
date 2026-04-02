// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Guest", {
	refresh(frm) {
		if (!frm.is_new()) {
			// VIP badge
			if (frm.doc.vip_code && frm.doc.vip_code !== "None") {
				frm.page.set_indicator(frm.doc.vip_code, "purple");
			}

			// Loyalty
			if (frm.doc.loyalty_points) {
				frm.dashboard.add_indicator(
					__("Points: {0}", [frm.doc.loyalty_points]), "blue"
				);
			}
			if (frm.doc.total_stays) {
				frm.dashboard.add_indicator(
					__("Stays: {0}", [frm.doc.total_stays]), "green"
				);
			}

			// Quick actions
			frm.add_custom_button(__("New Reservation"), () => {
				frappe.new_doc("VL Reservation", { guest: frm.doc.name });
			}, __("Actions"));

			frm.add_custom_button(__("Stay History"), () => {
				frappe.set_route("List", "VL Reservation", { guest: frm.doc.name });
			}, __("View"));

			if (frm.doc.customer) {
				frm.add_custom_button(__("Customer"), () => {
					frappe.set_route("Form", "Customer", frm.doc.customer);
				}, __("View"));
			}
		}
	},

	first_name(frm) { set_guest_name(frm); },
	last_name(frm) { set_guest_name(frm); },
});

function set_guest_name(frm) {
	let parts = [frm.doc.first_name || "", frm.doc.last_name || ""];
	frm.set_value("guest_name", parts.filter(Boolean).join(" "));
}
