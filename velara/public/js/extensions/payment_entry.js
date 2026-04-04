// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

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
