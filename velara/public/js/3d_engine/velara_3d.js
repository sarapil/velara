// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// License: GPL-3.0

/**
 * Velara 3D Hotel Integration
 * =============================
 * Integrates frappe_visual's 3D framework with Velara hospitality management.
 * Provides interactive 3D hotel floor plans with real-time room status,
 * wayfinding paths, and virtual tour capability.
 *
 * Lazy-loaded via frappe.require() — NOT included in app_include_js.
 *
 * Usage:
 *   await frappe.velara.floorPlan.create("#container", { property: "PROP-001" });
 */

frappe.provide("frappe.velara.floorPlan");

frappe.velara.floorPlan = {
	_loaded: false,

	async load() {
		if (this._loaded) return;
		await frappe.visual.load3D();
		this._loaded = true;
	},

	/**
	 * Create a 3D floor plan viewer with real-time room status.
	 * @param {string|Element} container — CSS selector or DOM element
	 * @param {Object} opts — { property, floor, modelUrl }
	 */
	async create(container, opts = {}) {
		await this.load();

		const el = typeof container === "string" ? document.querySelector(container) : container;
		if (!el) return;

		const { ThreeEngine, HospitalityOverlay } = frappe.visual.three;

		const engine = new ThreeEngine(el, {
			background: opts.background || "#faf9f6",
			shadows: true,
			antialias: true,
		});
		engine.init();

		// Apply hospitality overlay
		const overlay = new HospitalityOverlay(engine, {
			statusColors: {
				available: 0x22c55e,
				occupied: 0xef4444,
				cleaning: 0xf59e0b,
				maintenance: 0x6b7280,
				reserved: 0x3b82f6,
				checkout: 0xa855f7,
			},
		});

		// Load floor model if provided
		if (opts.modelUrl) {
			const { ModelLoader } = frappe.visual.three;
			const loader = new ModelLoader(engine);
			try {
				const model = await loader.load(opts.modelUrl);
				engine.scene.add(model);
			} catch (e) {
				console.error("Failed to load floor plan model:", e);
			}
		}

		// Load room status data from Velara
		if (opts.property) {
			try {
				const filters = { property: opts.property };
				if (opts.floor) filters.floor_number = opts.floor;

				const rooms = await frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "VL Room",
						filters,
						fields: ["name", "room_number", "room_type", "status",
							"floor_number", "mesh_name", "current_guest"],
						limit_page_length: 0,
					},
				});

				if (rooms.message) {
					const units = rooms.message.map(r => ({
						id: r.name,
						meshName: r.mesh_name || r.room_number,
						status: (r.status || "available").toLowerCase(),
						label: `${r.room_number} — ${__(r.room_type || "Standard")}`,
						metadata: {
							guest: r.current_guest,
							type: r.room_type,
						},
					}));
					overlay.registerUnits(units);
				}
			} catch (e) {
				console.warn("Could not load VL Room data:", e);
			}
		}

		// Click handler — show room details
		overlay.onUnitClick = (unitData) => {
			if (!unitData) return;
			frappe.set_route("Form", "VL Room", unitData.id);
		};

		return { engine, overlay };
	},

	/**
	 * Create a full dashboard with 3D floor plan + room status panel.
	 */
	async createDashboard(container, opts = {}) {
		const el = typeof container === "string" ? document.querySelector(container) : container;
		if (!el) return;

		el.innerHTML = `
			<div class="vl-floor-dashboard fv-fx-page-enter" style="display:flex;gap:16px;height:500px;">
				<div class="vl-floor-viewer" style="flex:3;border-radius:12px;overflow:hidden;border:1px solid var(--border-color);"></div>
				<div class="vl-floor-stats fv-fx-glass" style="flex:1;padding:16px;border-radius:12px;overflow-y:auto;">
					<h4>${__("Room Status")}</h4>
					<div class="vl-stats-content"></div>
				</div>
			</div>
		`;

		const viewerEl = el.querySelector(".vl-floor-viewer");
		const statsEl = el.querySelector(".vl-stats-content");

		const result = await this.create(viewerEl, opts);
		if (!result) return;

		// Build occupancy stats
		const summary = result.overlay.getOccupancySummary();
		const statusLabels = {
			available: { label: __("Available"), color: "#22c55e" },
			occupied: { label: __("Occupied"), color: "#ef4444" },
			cleaning: { label: __("Cleaning"), color: "#f59e0b" },
			maintenance: { label: __("Maintenance"), color: "#6b7280" },
			reserved: { label: __("Reserved"), color: "#3b82f6" },
			checkout: { label: __("Check-out"), color: "#a855f7" },
		};

		let statsHTML = `
			<div style="margin-bottom:12px;">
				<div class="text-muted">${__("Total Rooms")}</div>
				<div style="font-size:2em;font-weight:bold;color:var(--primary);">${summary.total}</div>
			</div>
			<div style="margin-bottom:12px;">
				<div class="text-muted">${__("Occupancy Rate")}</div>
				<div style="font-size:1.5em;font-weight:bold;">${summary.occupancyRate}%</div>
			</div>
			<hr>
		`;

		for (const [status, info] of Object.entries(statusLabels)) {
			const count = summary.byStatus?.[status] || 0;
			statsHTML += `
				<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
					<span style="display:flex;align-items:center;gap:6px;">
						<span style="width:10px;height:10px;border-radius:50%;background:${info.color};display:inline-block;"></span>
						${info.label}
					</span>
					<strong>${count}</strong>
				</div>
			`;
		}
		statsEl.innerHTML = statsHTML;

		return result;
	},

	/**
	 * Add 3D Floor Plan button to VL Room form.
	 */
	addFormButton(frm) {
		frm.add_custom_button(__("3D Floor Plan"), async () => {
			const dialog = new frappe.ui.Dialog({
				title: __("Hotel Floor Plan — {0}", [frm.doc.property || ""]),
				size: "extra-large",
			});
			dialog.body.style.height = "600px";
			dialog.show();
			await frappe.velara.floorPlan.create(dialog.body, {
				property: frm.doc.property,
				floor: frm.doc.floor_number,
			});
		}, __("View"));
	},
};
