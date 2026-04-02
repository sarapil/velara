// Copyright (c) 2026, ARKAN and contributors
// For license information, please see license.txt

frappe.ui.form.on("VL Folio", {
	refresh(frm) {
		// Status indicator
		frm.page.set_indicator(frm.doc.status, {
			"Open": "blue", "Settled": "green", "Closed": "darkgrey", "Void": "red"
		}[frm.doc.status] || "grey");

		if (frm.doc.status === "Open" && frm.doc.docstatus === 0) {
			// Post Charge button
			frm.add_custom_button(__("Post Charge"), () => {
				let d = new frappe.ui.Dialog({
					title: __("Post Charge"),
					fields: [
						{ fieldname: "charge_type", fieldtype: "Select", label: __("Charge Type"),
						  options: "Room Charge\nF&B\nMinibar\nLaundry\nSpa\nParking\nDamage\nMiscellaneous", reqd: 1 },
						{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), reqd: 1 },
						{ fieldname: "description", fieldtype: "Data", label: __("Description") },
					],
					primary_action(values) {
						frm.call("post_charge", values).then(() => { d.hide(); frm.reload_doc(); });
					}
				});
				d.show();
			}, __("Actions"));

			// Post Payment button
			frm.add_custom_button(__("Post Payment"), () => {
				let d = new frappe.ui.Dialog({
					title: __("Post Payment"),
					fields: [
						{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), reqd: 1 },
						{ fieldname: "payment_method", fieldtype: "Select", label: __("Method"),
						  options: "Cash\nCredit Card\nBank Transfer\nCity Ledger", default: "Cash" },
					],
					primary_action(values) {
						frm.call("post_payment", values).then(() => { d.hide(); frm.reload_doc(); });
					}
				});
				d.show();
			}, __("Actions"));

			// Create Sales Invoice
			frm.add_custom_button(__("Create Invoice"), () => {
				frm.call("create_sales_invoice").then(r => {
					if (r.message) {
						frappe.set_route("Form", "Sales Invoice", r.message);
					}
				});
			}, __("Actions"));
		}

		// Balance display
		if (!frm.is_new()) {
			let color = flt(frm.doc.balance) > 0 ? "red" : "green";
			frm.dashboard.add_indicator(
				__("Balance: {0}", [format_currency(frm.doc.balance)]), color
			);
		}
	}
});

frappe.ui.form.on("VL Folio Charge", {
	amount(frm) { frm.trigger("calculate_totals"); },
	charges_remove(frm) { frm.trigger("calculate_totals"); },
});
