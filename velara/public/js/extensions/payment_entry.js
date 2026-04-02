/**
 * VELARA — Payment Entry DocType Extension
 * Shows folio settlement info
 */
frappe.ui.form.on("Payment Entry", {
	refresh: function (frm) {
		if (!frappe.boot.velara || !frappe.boot.velara.has_access) return;
		// Folio settlement info shown via custom fields if linked
	},
});
