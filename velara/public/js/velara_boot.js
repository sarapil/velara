/**
 * VELARA Hotel Management — Boot Script
 * Initializes client-side configuration and global namespace
 */

// Global Velara namespace
window.velara = window.velara || {};

frappe.provide("velara");
frappe.provide("velara.utils");
frappe.provide("velara.ui");

// ========================================
// Boot Initialization
// ========================================
$(document).on("startup", function () {
	if (!frappe.boot.velara) return;

	velara.config = frappe.boot.velara;
	velara.has_access = velara.config.has_access;
	velara.roles = velara.config.roles || [];
	velara.features = velara.config.features || {};

	// Set CSS custom properties from config if needed
	document.documentElement.style.setProperty("--vl-gold", "#C9A84C");
	document.documentElement.style.setProperty("--vl-navy", "#1B2A4A");
});

// ========================================
// Utility Functions
// ========================================

/**
 * Format room status as colored badge
 */
velara.utils.roomStatusBadge = function (status) {
	const colors = {
		Available: "green",
		Occupied: "red",
		Reserved: "blue",
		Blocked: "gray",
		"Out of Order": "orange",
		"Out of Service": "yellow",
	};
	const color = colors[status] || "gray";
	return `<span class="indicator-pill ${color}">${__(status)}</span>`;
};

/**
 * Format HK status as colored badge
 */
velara.utils.hkStatusBadge = function (status) {
	const colors = {
		Clean: "green",
		Dirty: "red",
		Inspected: "blue",
		"Out of Order": "orange",
		Pickup: "yellow",
	};
	const color = colors[status] || "gray";
	return `<span class="indicator-pill ${color}">${__(status)}</span>`;
};

/**
 * Format reservation status
 */
velara.utils.reservationStatusBadge = function (status) {
	const colors = {
		Draft: "gray",
		Confirmed: "blue",
		"Checked In": "green",
		"Checked Out": "darkgrey",
		Cancelled: "red",
		"No Show": "orange",
		Waitlist: "yellow",
	};
	const color = colors[status] || "gray";
	return `<span class="indicator-pill ${color}">${__(status)}</span>`;
};

/**
 * Format VIP code as badge
 */
velara.utils.vipBadge = function (vip_code) {
	if (!vip_code || vip_code === "None") return "";
	const styles = {
		"VIP 1": "vip-1",
		"VIP 2": "vip-2",
		"VIP 3": "vip-3",
		Celebrity: "celebrity",
		Blacklist: "blacklist",
	};
	const cls = styles[vip_code] || "";
	return `<span class="vl-vip-badge ${cls}">${__(vip_code)}</span>`;
};

/**
 * Format loyalty tier
 */
velara.utils.loyaltyBadge = function (tier) {
	if (!tier || tier === "None") return "";
	return `<span class="vl-tier-badge ${tier.toLowerCase()}">${__(tier)}</span>`;
};

/**
 * Calculate night count between dates
 */
velara.utils.nightCount = function (check_in, check_out) {
	if (!check_in || !check_out) return 0;
	const d1 = frappe.datetime.str_to_obj(check_in);
	const d2 = frappe.datetime.str_to_obj(check_out);
	return Math.max(0, Math.round((d2 - d1) / (1000 * 60 * 60 * 24)));
};

/**
 * Quick room availability check
 */
velara.utils.checkAvailability = function (check_in, check_out, room_type, callback) {
	frappe.call({
		method: "velara.api.reservation.check_availability",
		args: { check_in_date: check_in, check_out_date: check_out, room_type: room_type },
		callback: function (r) {
			if (callback) callback(r.message);
		},
	});
};

// ========================================
// UI Components
// ========================================

/**
 * Show room status popup
 */
velara.ui.showRoomPopup = function (room) {
	frappe.call({
		method: "velara.api.room.get_floor_map",
		callback: function (r) {
			if (r.message) {
				// Open floor map dialog
				velara.ui._renderFloorMap(r.message);
			}
		},
	});
};

/**
 * Quick check-in dialog
 */
velara.ui.quickCheckIn = function (reservation_name) {
	frappe.new_doc("VL Check In", { reservation: reservation_name });
};

/**
 * Quick check-out dialog
 */
velara.ui.quickCheckOut = function (reservation_name) {
	frappe.new_doc("VL Check Out", { reservation: reservation_name });
};

/**
 * Post charge to folio dialog
 */
velara.ui.postCharge = function (folio_name) {
	const d = new frappe.ui.Dialog({
		title: __("Post Charge"),
		fields: [
			{ fieldname: "charge_type", fieldtype: "Select", label: __("Charge Type"), reqd: 1,
				options: "Room Charge\nFood & Beverage\nMinibar\nLaundry\nTelephone\nSpa\nParking\nInternet\nRoom Service\nDamage\nMisc" },
			{ fieldname: "description", fieldtype: "Data", label: __("Description") },
			{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), reqd: 1 },
		],
		primary_action_label: __("Post"),
		primary_action: function (values) {
			frappe.call({
				method: "velara.utils.post_charge_to_folio",
				args: {
					folio_name: folio_name,
					charge_type: values.charge_type,
					amount: values.amount,
					description: values.description,
				},
				callback: function () {
					d.hide();
					frappe.show_alert({ message: __("Charge posted"), indicator: "green" });
					cur_frm && cur_frm.reload_doc();
				},
			});
		},
	});
	d.show();
};

// ========================================
// List View Formatters
// ========================================
frappe.listview_settings["VL Room"] = {
	get_indicator: function (doc) {
		const colors = {
			Available: [__("Available"), "green", "room_status,=,Available"],
			Occupied: [__("Occupied"), "red", "room_status,=,Occupied"],
			Reserved: [__("Reserved"), "blue", "room_status,=,Reserved"],
			Blocked: [__("Blocked"), "gray", "room_status,=,Blocked"],
			"Out of Order": [__("Out of Order"), "orange", "room_status,=,Out of Order"],
			"Out of Service": [__("Out of Service"), "yellow", "room_status,=,Out of Service"],
		};
		return colors[doc.room_status] || [__(doc.room_status), "gray", ""];
	},
};

frappe.listview_settings["VL Reservation"] = {
	get_indicator: function (doc) {
		const colors = {
			Draft: [__("Draft"), "gray", "status,=,Draft"],
			Confirmed: [__("Confirmed"), "blue", "status,=,Confirmed"],
			"Checked In": [__("Checked In"), "green", "status,=,Checked In"],
			"Checked Out": [__("Checked Out"), "darkgrey", "status,=,Checked Out"],
			Cancelled: [__("Cancelled"), "red", "status,=,Cancelled"],
			"No Show": [__("No Show"), "orange", "status,=,No Show"],
			Waitlist: [__("Waitlist"), "yellow", "status,=,Waitlist"],
		};
		return colors[doc.status] || [__(doc.status), "gray", ""];
	},
};

frappe.listview_settings["VL HK Task"] = {
	get_indicator: function (doc) {
		const colors = {
			Pending: [__("Pending"), "orange", "status,=,Pending"],
			"In Progress": [__("In Progress"), "blue", "status,=,In Progress"],
			Completed: [__("Completed"), "green", "status,=,Completed"],
			Inspected: [__("Inspected"), "cyan", "status,=,Inspected"],
			Rejected: [__("Rejected"), "red", "status,=,Rejected"],
		};
		return colors[doc.status] || [__(doc.status), "gray", ""];
	},
};

frappe.listview_settings["VL Folio"] = {
	get_indicator: function (doc) {
		const colors = {
			Open: [__("Open"), "blue", "status,=,Open"],
			Settled: [__("Settled"), "green", "status,=,Settled"],
			Closed: [__("Closed"), "darkgrey", "status,=,Closed"],
			Void: [__("Void"), "red", "status,=,Void"],
		};
		return colors[doc.status] || [__(doc.status), "gray", ""];
	},
};

frappe.listview_settings["VL Maintenance Request"] = {
	get_indicator: function (doc) {
		const colors = {
			Open: [__("Open"), "red", "status,=,Open"],
			Assigned: [__("Assigned"), "orange", "status,=,Assigned"],
			"In Progress": [__("In Progress"), "blue", "status,=,In Progress"],
			"On Hold": [__("On Hold"), "yellow", "status,=,On Hold"],
			Completed: [__("Completed"), "green", "status,=,Completed"],
			Cancelled: [__("Cancelled"), "gray", "status,=,Cancelled"],
		};
		return colors[doc.status] || [__(doc.status), "gray", ""];
	},
};

frappe.listview_settings["VL Service Request"] = {
	get_indicator: function (doc) {
		const colors = {
			Open: [__("Open"), "red", "status,=,Open"],
			"In Progress": [__("In Progress"), "blue", "status,=,In Progress"],
			Completed: [__("Completed"), "green", "status,=,Completed"],
			Cancelled: [__("Cancelled"), "gray", "status,=,Cancelled"],
		};
		return colors[doc.status] || [__(doc.status), "gray", ""];
	},
};
