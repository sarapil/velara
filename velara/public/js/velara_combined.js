/* velara — Combined JS (reduces HTTP requests) */
/* Auto-generated from 3 individual files */


/* === velara_boot.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

/**
 * VELARA Hotel Management — Boot Script
 * Initializes client-side configuration and global namespace
 */

// Global Velara namespace
window.velara = window.velara || {};

// Guard: skip if frappe core not loaded (transient HTTP/2 proxy failures)
if (typeof frappe === "undefined" || typeof frappe.provide !== "function") {
	window.frappe = window.frappe || {};
	frappe.provide = frappe.provide || function () {};
}
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

// ========================================
// FloatingWindow Onboarding Launcher
// ========================================

/**
 * Opens the Velara onboarding tutorial inside a frappe.visual.floatingWindow
 * on the opposite side of the sidebar (right in LTR, left in RTL).
 */
velara.open_onboarding = function () {
	if (velara._onboarding_win && velara._onboarding_win.is_visible) {
		velara._onboarding_win.focus();
		return;
	}

	const is_rtl = document.documentElement.dir === "rtl" || $("html").attr("dir") === "rtl";

	const open_win = () => {
		if (frappe.visual && frappe.visual.floatingWindow) {
			velara._onboarding_win = frappe.visual.floatingWindow({
				title: __("Velara Onboarding"),
				width: 520,
				height: 600,
				position: is_rtl ? "left" : "right",
				resizable: true,
				minimizable: true,
				maximizable: true,
				content: '<div class="vl-fw-onboarding" style="padding:16px;"></div>',
				on_close() {
					velara._onboarding_win = null;
				},
			});

			setTimeout(() => {
				const container = velara._onboarding_win?.$body
					? velara._onboarding_win.$body.find(".vl-fw-onboarding")[0]
					: document.querySelector(".vl-fw-onboarding");

				if (!container) return;
				_render_velara_onboarding(container);
			}, 200);
		} else {
			frappe.set_route("app", "velara-onboarding");
		}
	};

	if (!frappe.visual || !frappe.visual.floatingWindow) {
		frappe.require("frappe_visual.bundle.js", open_win);
	} else {
		open_win();
	}
};

function _vl_screen_link(icon, title, desc, route) {
	return `<a href="/app/${route}" class="vl-onb-link" style="display:flex;align-items:center;gap:12px;padding:10px 12px;border:1px solid var(--border-color);border-radius:8px;text-decoration:none;color:inherit;transition:all .2s;">
		<span style="font-size:24px;">${icon}</span>
		<div><b>${title}</b><br><span class="text-muted" style="font-size:12px;">${desc}</span></div>
	</a>`;
}

function _render_velara_onboarding(container) {
	const steps = [
		{
			title: __("Welcome to Velara"),
			html: `<div class="text-center" style="padding:24px 0;">
				<img src="/assets/velara/images/velara-logo.svg" style="width:80px;height:80px;margin-bottom:16px;" onerror="this.style.display='none'">
				<h3 style="color:var(--vl-gold,#C9A84C);">${__("Hotel Property Management")}</h3>
				<p class="text-muted">${__("Manage your hotel operations — reservations, check-in/out, housekeeping, billing, and guest relations")}</p>
				<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:16px;">
					<span class="badge badge-primary">${__("38+ DocTypes")}</span>
					<span class="badge badge-info">${__("14 Modules")}</span>
					<span class="badge badge-success">${__("8 Workflows")}</span>
					<span class="badge badge-warning">${__("6 Roles")}</span>
				</div>
			</div>`,
		},
		{
			title: __("Your Key Screens"),
			html: `<div style="display:grid;gap:12px;">
				${_vl_screen_link("🏨", __("Front Desk"), __("Real-time room status & check-ins"), "velara-front-desk")}
				${_vl_screen_link("📅", __("Reservations"), __("Manage bookings & availability"), "vl-reservation")}
				${_vl_screen_link("🧹", __("Housekeeping"), __("Room cleaning tasks & inspections"), "vl-hk-task")}
				${_vl_screen_link("💳", __("Guest Folios"), __("Billing, charges, & settlements"), "vl-folio")}
				${_vl_screen_link("📊", __("Dashboard"), __("Occupancy & revenue analytics"), "velara-dashboard")}
			</div>`,
		},
		{
			title: __("Quick Start"),
			html: `<div style="padding:8px 0;">
				<div style="display:flex;flex-direction:column;gap:16px;">
					<div style="display:flex;align-items:center;gap:12px;">
						<div style="width:32px;height:32px;border-radius:50%;background:var(--vl-gold,#C9A84C);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">1</div>
						<div><b>${__("Setup Room Types & Rooms")}</b><br><span class="text-muted">${__("Define your property layout and room categories")}</span></div>
					</div>
					<div style="display:flex;align-items:center;gap:12px;">
						<div style="width:32px;height:32px;border-radius:50%;background:var(--vl-gold,#C9A84C);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">2</div>
						<div><b>${__("Create Reservations")}</b><br><span class="text-muted">${__("Book guests into available rooms with rates")}</span></div>
					</div>
					<div style="display:flex;align-items:center;gap:12px;">
						<div style="width:32px;height:32px;border-radius:50%;background:var(--vl-gold,#C9A84C);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">3</div>
						<div><b>${__("Check In & Manage Stay")}</b><br><span class="text-muted">${__("Process arrivals, post charges, handle requests")}</span></div>
					</div>
					<div style="display:flex;align-items:center;gap:12px;">
						<div style="width:32px;height:32px;border-radius:50%;background:var(--vl-gold,#C9A84C);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">4</div>
						<div><b>${__("Check Out & Settle Folio")}</b><br><span class="text-muted">${__("Complete billing and generate invoice")}</span></div>
					</div>
				</div>
			</div>`,
		},
	];

	let current = 0;

	function render_step() {
		const step = steps[current];
		const nav_prev = current > 0
			? `<button class="btn btn-xs btn-default vl-onb-prev">${__("Previous")}</button>` : "";
		const nav_next = current < steps.length - 1
			? `<button class="btn btn-xs btn-primary vl-onb-next">${__("Next")}</button>`
			: `<button class="btn btn-xs btn-success vl-onb-done">${__("Get Started!")}</button>`;

		container.innerHTML = `
			<div style="margin-bottom:8px;">
				<span class="text-muted" style="font-size:11px;">${__("Step")} ${current + 1} / ${steps.length}</span>
				<div style="height:3px;background:var(--border-color);border-radius:2px;margin-top:4px;">
					<div style="height:100%;width:${((current + 1) / steps.length) * 100}%;background:var(--vl-gold,#C9A84C);border-radius:2px;transition:width .3s;"></div>
				</div>
			</div>
			<h5 style="margin:12px 0 8px;">${step.title}</h5>
			${step.html}
			<div style="display:flex;justify-content:space-between;margin-top:16px;">
				${nav_prev} <span></span> ${nav_next}
			</div>
		`;

		container.querySelector(".vl-onb-prev")?.addEventListener("click", () => { current--; render_step(); });
		container.querySelector(".vl-onb-next")?.addEventListener("click", () => { current++; render_step(); });
		container.querySelector(".vl-onb-done")?.addEventListener("click", () => {
			if (velara._onboarding_win) velara._onboarding_win.close();
			frappe.set_route("velara-dashboard");
		});
	}

	render_step();
}


/* === fv_integration.js === */
// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT
// frappe_visual Integration for Velara

(function() {
    "use strict";

    // App branding registration
    const APP_CONFIG = {
        name: "velara",
        title: "Velara",
        color: "#8B5CF6",
        module: "Velara Front Desk",
    };

    // Initialize visual enhancements when ready
    $(document).on("app_ready", function() {
        // Register app color with visual theme system
        if (frappe.visual && frappe.visual.ThemeManager) {
            try {
                document.documentElement.style.setProperty(
                    "--velara-primary",
                    APP_CONFIG.color
                );
            } catch(e) {}
        }

        // Initialize bilingual tooltips for Arabic support
        if (frappe.visual && frappe.visual.bilingualTooltip) {
            // bilingualTooltip auto-initializes — just ensure it's active
        }
    });

    // Route-based visual page rendering
    $(document).on("page-change", function() {
        if (!frappe.visual || !frappe.visual.generator) return;

    // Visual Settings Page
    if (frappe.get_route_str() === 'velara-settings') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.settingsPage(
                page.main[0] || page.main,
                "VL Settings"
            );
        }
    }

    // Visual Reports Hub
    if (frappe.get_route_str() === 'velara-reports') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.reportsHub(
                page.main[0] || page.main,
                "Velara Front Desk"
            );
        }
    }
    });
})();


/* === velara_scene.js === */
// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT

/**
 * Velara Scene Dashboard — Immersive SVG workspace header
 * Uses ScenePresetCafe with live hospitality KPI data binding
 *
 * Usage: velara.scene_dashboard.render("#workspace-header")
 */

frappe.provide("velara.scene_dashboard");

velara.scene_dashboard = {
	async render(container_selector) {
		const container = typeof container_selector === "string"
			? document.querySelector(container_selector)
			: container_selector;

		if (!container) return;

		// Lazy-load frappe_visual bundle
		if (!frappe.visual || !frappe.visual.scenePresetCafe) {
			await new Promise((resolve) =>
				frappe.require("frappe_visual.bundle.js", resolve)
			);
		}

		// Graceful degradation
		if (!frappe.visual || !frappe.visual.scenePresetCafe) {
			container.innerHTML = `<div class="fv-fx-glass" style="padding:24px;text-align:center;">
				<h4 style="color:var(--vl-gold,#C9A84C);">${__("Velara Hospitality")}</h4>
				<p class="text-muted">${__("Scene dashboard requires frappe_visual")}</p>
			</div>`;
			return;
		}

		const scene = await frappe.visual.scenePresetCafe({
			container: container,
			theme: "warm",
			frames: [
				{ label: __("Occupancy Rate"), value: "...", status: "info" },
				{ label: __("Today's Revenue"), value: "...", status: "success" },
				{ label: __("Check-ins Today"), value: "...", status: "info" },
				{ label: __("Pending HK Tasks"), value: "...", status: "warning" },
			],
			documents: [
				{
					label: __("Arrivals Today"),
					count: 0,
					href: "/app/vl-reservation?check_in_date=" + frappe.datetime.get_today(),
					color: "#10b981",
				},
				{
					label: __("Departures Today"),
					count: 0,
					href: "/app/vl-reservation?check_out_date=" + frappe.datetime.get_today(),
					color: "#f59e0b",
				},
			],
			books: [
				{ label: __("Reports"), href: "/app/query-report", color: "#C9A84C" },
				{ label: __("Rate Plans"), href: "/app/vl-rate-plan", color: "#6366f1" },
			],
		});

		// Bind live data
		if (frappe.visual.sceneDataBinder) {
			await frappe.visual.sceneDataBinder({
				engine: scene,
				frames: [
					{
						label: __("Occupancy Rate"),
						doctype: "VL Room",
						aggregate: "percent",
						field: "room_status",
						match_value: "Occupied",
						format: "%s%",
						status_rules: { ">80": "success", ">50": "info", "<=50": "warning" },
					},
					{
						label: __("Today's Revenue"),
						doctype: "VL Folio",
						aggregate: "sum",
						field: "total_amount",
						filters: { posting_date: frappe.datetime.get_today(), status: "Settled" },
						format: "$%s",
						status_rules: { ">5000": "success", ">1000": "info", "<=1000": "warning" },
					},
					{
						label: __("Check-ins Today"),
						doctype: "VL Check In",
						aggregate: "count",
						filters: { check_in_date: frappe.datetime.get_today() },
						status_rules: { ">10": "success", ">5": "info", "<=5": "warning" },
					},
					{
						label: __("Pending HK Tasks"),
						doctype: "VL HK Task",
						aggregate: "count",
						filters: { status: "Pending" },
						status_rules: { ">10": "danger", ">5": "warning", "<=5": "success" },
					},
				],
				refreshInterval: 30000,
			});
		}

		return scene;
	},
};

