/**
 * VELARA — POS Invoice Extension
 * Post-to-Room functionality
 */
frappe.ui.form.on("POS Invoice", {
	refresh: function (frm) {
		if (!frappe.boot.velara || !frappe.boot.velara.has_access) return;

		if (!frm.is_new() && frm.doc.docstatus === 1) {
			frm.add_custom_button(
				__("Post to Room"),
				function () {
					const d = new frappe.ui.Dialog({
						title: __("Post to Guest Folio"),
						fields: [
							{
								fieldname: "room",
								fieldtype: "Link",
								options: "VL Room",
								label: __("Room"),
								reqd: 1,
								get_query: function () {
									return {
										filters: { room_status: "Occupied" },
									};
								},
							},
						],
						primary_action_label: __("Post"),
						primary_action: function (values) {
							frappe.call({
								method: "velara.events.pos_events.post_pos_to_folio",
								args: {
									pos_invoice: frm.doc.name,
									room: values.room,
								},
								callback: function (r) {
									d.hide();
									if (r.message) {
										frappe.show_alert({
											message: __("Posted to Folio {0}", [r.message]),
											indicator: "green",
										});
									}
								},
							});
						},
					});
					d.show();
				},
				__("Velara")
			);
		}
	},
});
