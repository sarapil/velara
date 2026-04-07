// Copyright (c) 2026, Arkan Lab — License: MIT
frappe.listview_settings["VL Reservation"] = {
	add_fields: ["status", "room", "nights", "check_in_date", "check_out_date", "net_total"],
	get_indicator(doc) {
		const map = {
			Draft: [__("Draft"), "orange", "status,=,Draft"],
			Tentative: [__("Tentative"), "blue", "status,=,Tentative"],
			Confirmed: [__("Confirmed"), "green", "status,=,Confirmed"],
			Guaranteed: [__("Guaranteed"), "purple", "status,=,Guaranteed"],
			"Checked In": [__("Checked In"), "green", "status,=,Checked In"],
			"Checked Out": [__("Checked Out"), "grey", "status,=,Checked Out"],
			Cancelled: [__("Cancelled"), "red", "status,=,Cancelled"],
			"No Show": [__("No Show"), "red", "status,=,No Show"],
		};
		return map[doc.status] || [__(doc.status), "grey", `status,=,${doc.status}`];
	},
	formatters: {
		net_total(val) {
			return val ? format_currency(val) : "";
		},
	},
};
