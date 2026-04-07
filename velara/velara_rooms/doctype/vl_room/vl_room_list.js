// Copyright (c) 2026, Arkan Lab — License: MIT
frappe.listview_settings["VL Room"] = {
	add_fields: ["room_status", "room_type", "property", "floor_number", "current_guest"],
	get_indicator(doc) {
		const map = {
			Available: [__("Available"), "green", "room_status,=,Available"],
			Occupied: [__("Occupied"), "red", "room_status,=,Occupied"],
			Reserved: [__("Reserved"), "blue", "room_status,=,Reserved"],
			Dirty: [__("Dirty"), "orange", "room_status,=,Dirty"],
			Clean: [__("Clean"), "green", "room_status,=,Clean"],
			Inspected: [__("Inspected"), "grey", "room_status,=,Inspected"],
			"Out of Order": [__("Out of Order"), "red", "room_status,=,Out of Order"],
			"Out of Service": [__("Out of Service"), "grey", "room_status,=,Out of Service"],
		};
		return map[doc.room_status] || [__(doc.room_status), "grey", `room_status,=,${doc.room_status}`];
	},
};
