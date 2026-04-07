// Copyright (c) 2026, Arkan Lab — License: GPL-3.0

frappe.pages["velara-floor-map"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("3D Floor Map"),
		single_column: true,
	});

	frappe.breadcrumbs.add("Velara");
	page.main.css({ "min-height": "calc(100vh - 120px)", padding: 0, overflow: "hidden" });

	wrapper._page = page;
	wrapper._floorMap = new VelaraFloorMap(page);
};

frappe.pages["velara-floor-map"].refresh = function (wrapper) {
	wrapper._floorMap?.refresh();
};

class VelaraFloorMap {
	constructor(page) {
		this.page = page;
		this.$container = $(page.body);
		this.viewer = null;
		this.currentProperty = null;
		this.currentFloor = null;
		this.autoRefreshTimer = null;

		this.setupActions();
		this.renderSkeleton();
	}

	setupActions() {
		this.propertyField = this.page.add_field({
			fieldname: "property",
			label: __("Property"),
			fieldtype: "Link",
			options: "VL Property",
			change: () => {
				this.currentProperty = this.propertyField.get_value();
				if (this.currentProperty) this.loadFloorMap();
			},
		});

		this.floorField = this.page.add_field({
			fieldname: "floor",
			label: __("Floor"),
			fieldtype: "Select",
			options: "",
			change: () => {
				this.currentFloor = this.floorField.get_value();
				if (this.currentFloor) this.loadFloorMap();
			},
		});

		this.page.set_secondary_action(__("Refresh"), () => this.refresh(), "refresh-cw");

		this.page.add_inner_button(__("Auto-refresh ON"), () => this.toggleAutoRefresh());
		this.page.add_action_item(__("Screenshot"), () => this.takeScreenshot());
		this.page.add_action_item(__("Full Screen"), () => this.toggleFullScreen());

		// XR integration — VR hotel tour + AR floor review
		frappe.base_base?.xr_mixin?.attach(this, {
			get_engine: () => this.viewer?.engine,
			get_spatial_data: () => this.getXRPanels(),
			vr_options: { startPosition: [0, 1.7, 8] },
		});
	}

	getXRPanels() {
		const stats = this.page.main?.find(".vl-floor-stats").text() || "";
		return [
			{ content: `<h3>${__("Floor Overview")}</h3><p>${stats.substring(0, 100)}</p>`, position: [0, 2.5, -4], billboard: true },
		];
	}

	renderSkeleton() {
		this.$container.html(`
			<div class="vl-floor-map-page" style="height:calc(100vh - 160px);display:flex;">
				<div class="vl-floor-viewport" style="flex:3;position:relative;"></div>
				<div class="vl-floor-sidebar fv-fx-glass"
					style="flex:0 0 300px;padding:16px;overflow-y:auto;border-inline-start:1px solid var(--border-color);">
					<h4>${__("Room Status Overview")}</h4>
					<div class="vl-floor-stats"></div>
					<hr>
					<h5>${__("Quick Filters")}</h5>
					<div class="vl-status-filters" style="display:flex;flex-direction:column;gap:6px;"></div>
					<hr>
					<h5>${__("Selected Room")}</h5>
					<div class="vl-room-detail">
						<p class="text-muted">${__("Click a room in the 3D view")}</p>
					</div>
					<hr>
					<h5>${__("Housekeeping Queue")}</h5>
					<div class="vl-hk-queue"></div>
				</div>
			</div>
		`);
	}

	async loadFloorMap() {
		if (!this.currentProperty) return;

		const viewport = this.$container.find(".vl-floor-viewport")[0];

		// Clean up previous viewer
		if (this.viewer) {
			this.viewer.engine?.dispose();
			this.viewer = null;
		}

		viewport.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;"><div class="text-muted">${__("Loading 3D floor map...")}</div></div>`;

		try {
			await frappe.require("/assets/velara/js/3d_engine/velara_3d.js");

			viewport.innerHTML = "";
			this.viewer = await frappe.velara.floorPlan.create(viewport, {
				property: this.currentProperty,
				floor: this.currentFloor || undefined,
			});

			if (this.viewer) {
				// Override click handler to show detail in sidebar
				this.viewer.overlay.onUnitClick = (unit) => this.showRoomDetail(unit);
			}

			// Build stats sidebar
			await this.buildStatsSidebar();
			await this.loadHousekeepingQueue();

		} catch (e) {
			viewport.innerHTML = `<div style="text-align:center;padding:40px;"><div class="text-danger">${__("Error loading floor map")}</div></div>`;
			console.error(e);
		}
	}

	async buildStatsSidebar() {
		const statsEl = this.$container.find(".vl-floor-stats");
		const filtersEl = this.$container.find(".vl-status-filters");

		if (!this.viewer) return;

		const summary = this.viewer.overlay.getOccupancySummary();
		const statuses = [
			{ key: "available", label: __("Available"), color: "#22c55e" },
			{ key: "occupied", label: __("Occupied"), color: "#ef4444" },
			{ key: "cleaning", label: __("Cleaning"), color: "#f59e0b" },
			{ key: "maintenance", label: __("Maintenance"), color: "#6b7280" },
			{ key: "reserved", label: __("Reserved"), color: "#3b82f6" },
			{ key: "checkout", label: __("Check-out"), color: "#a855f7" },
		];

		statsEl.html(`
			<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">
				<div class="fv-fx-hover-lift" style="text-align:center;padding:12px;border-radius:8px;background:var(--bg-light-gray);">
					<div style="font-size:2em;font-weight:bold;color:var(--primary);">${summary.total || 0}</div>
					<div class="text-muted">${__("Total")}</div>
				</div>
				<div class="fv-fx-hover-lift" style="text-align:center;padding:12px;border-radius:8px;background:var(--bg-light-gray);">
					<div style="font-size:2em;font-weight:bold;">${summary.occupancyRate || 0}%</div>
					<div class="text-muted">${__("Occupancy")}</div>
				</div>
			</div>
		`);

		filtersEl.html(statuses.map(s => `
			<label class="vl-filter-label" style="display:flex;align-items:center;gap:8px;cursor:pointer;">
				<input type="checkbox" class="vl-status-filter" data-status="${s.key}" checked>
				<span style="width:12px;height:12px;border-radius:50%;background:${s.color};display:inline-block;"></span>
				${s.label}
				<strong style="margin-inline-start:auto;">${summary.byStatus?.[s.key] || 0}</strong>
			</label>
		`).join(""));

		filtersEl.find(".vl-status-filter").on("change", () => {
			const visible = [];
			filtersEl.find(".vl-status-filter:checked").each(function () {
				visible.push($(this).data("status"));
			});
			this.viewer?.overlay?.filterByStatuses?.(visible);
		});
	}

	async loadHousekeepingQueue() {
		const queueEl = this.$container.find(".vl-hk-queue");
		try {
			const res = await frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "VL Room",
					filters: {
						property: this.currentProperty,
						room_status: ["in", ["Dirty", "Clean"]],
					},
					fields: ["name", "room_number", "room_status", "floor_number"],
					order_by: "room_status desc, room_number asc",
					limit_page_length: 20,
				},
			});

			if (res.message?.length) {
				queueEl.html(res.message.map(r => `
					<div class="fv-fx-hover-lift" style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;border-radius:6px;cursor:pointer;margin-bottom:4px;"
						onclick="frappe.set_route('Form','VL Room','${r.name}')">
						<span>${r.room_number}</span>
						<span class="indicator-pill ${r.room_status === "Dirty" ? "red" : "green"}">${__(r.room_status)}</span>
					</div>
				`).join(""));
			} else {
				queueEl.html(`<p class="text-muted">${__("All rooms are ready")}</p>`);
			}
		} catch (e) {
			queueEl.html(`<p class="text-muted">${__("Could not load queue")}</p>`);
		}
	}

	showRoomDetail(unitData) {
		const detail = this.$container.find(".vl-room-detail");
		if (!unitData) {
			detail.html(`<p class="text-muted">${__("Click a room in the 3D view")}</p>`);
			return;
		}

		detail.html(`
			<div class="fv-fx-hover-lift" style="padding:10px;border-radius:8px;">
				<h5>${unitData.label || unitData.id}</h5>
				<div class="indicator-pill ${unitData.status === "available" ? "green" : unitData.status === "occupied" ? "red" : "orange"}"
					style="margin-bottom:8px;">${__(unitData.status)}</div>
				${unitData.metadata?.guest ? `<div>${__("Guest")}: ${unitData.metadata.guest}</div>` : ""}
				${unitData.metadata?.type ? `<div>${__("Type")}: ${__(unitData.metadata.type)}</div>` : ""}
				<div style="margin-top:10px;display:flex;gap:6px;">
					<button class="btn btn-xs btn-primary" onclick="frappe.set_route('Form','VL Room','${unitData.id}')">${__("Open")}</button>
					${unitData.status === "available" ? `<button class="btn btn-xs btn-default" onclick="frappe.new_doc('VL Reservation',{room:'${unitData.id}'})">${__("Book")}</button>` : ""}
				</div>
			</div>
		`);
	}

	toggleAutoRefresh() {
		if (this.autoRefreshTimer) {
			clearInterval(this.autoRefreshTimer);
			this.autoRefreshTimer = null;
			frappe.show_alert({ message: __("Auto-refresh OFF"), indicator: "orange" });
		} else {
			this.autoRefreshTimer = setInterval(() => this.loadFloorMap(), 30000);
			frappe.show_alert({ message: __("Auto-refresh ON (30s)"), indicator: "green" });
		}
	}

	takeScreenshot() {
		if (!this.viewer?.engine?.renderer) return;
		const canvas = this.viewer.engine.renderer.domElement;
		const link = document.createElement("a");
		link.download = `velara-floor-${this.currentFloor || "all"}.png`;
		link.href = canvas.toDataURL("image/png");
		link.click();
	}

	toggleFullScreen() {
		const el = this.$container.find(".vl-floor-map-page")[0];
		if (!document.fullscreenElement) el.requestFullscreen?.();
		else document.exitFullscreen?.();
	}

	refresh() {
		this.loadFloorMap();
	}
}
