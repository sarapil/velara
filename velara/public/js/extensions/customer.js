// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * VELARA — Customer DocType Extension
 * Adds hotel guest info to Customer form
 */
frappe.ui.form.on("Customer", {
	refresh: function (frm) {
		if (!frappe.boot.velara || !frappe.boot.velara.has_access) return;

		// Show linked VL Guest info
		if (frm.doc.vl_guest) {
			frm.add_custom_button(
				__("View Guest Profile"),
				function () {
					frappe.set_route("Form", "VL Guest", frm.doc.vl_guest);
				},
				__("Velara")
			);
		} else if (!frm.is_new()) {
			frm.add_custom_button(
				__("Create Guest Profile"),
				function () {
					frappe.new_doc("VL Guest", {
						guest_name: frm.doc.customer_name,
						customer: frm.doc.name,
						email: frm.doc.email_id,
						mobile: frm.doc.mobile_no,
					});
				},
				__("Velara")
			);
		}

		// Show VIP badge if set
		if (frm.doc.vl_vip_code && frm.doc.vl_vip_code !== "None") {
			frm.set_intro(
				velara.utils.vipBadge(frm.doc.vl_vip_code) + " " + velara.utils.loyaltyBadge(frm.doc.vl_loyalty_tier),
				"blue"
			);
		}

		// Show quick reservation button
		if (!frm.is_new() && frm.doc.vl_guest) {
			frm.add_custom_button(
				__("New Reservation"),
				function () {
					frappe.new_doc("VL Reservation", { guest: frm.doc.vl_guest });
				},
				__("Velara")
			);
		}
	},
});
