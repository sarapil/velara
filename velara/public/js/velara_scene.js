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
