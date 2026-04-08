// Copyright (c) 2026, Arkan Lab — https://arkan.it.com
// License: MIT

/**
 * Velara Explorer — Hotel Relationship Graph
 *
 * Pick any hotel entity (Reservation, Room, Guest, Folio, Event)
 * and see ALL its relationships radiate outward. Double-click to re-center.
 */

frappe.pages["velara-explorer"].on_page_load = async function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Velara Explorer | مستكشف فيلارا"),
		single_column: true,
	});

	const DOCTYPES = [
		"VL Reservation", "VL Room", "VL Guest", "VL Folio",
		"VL Room Type", "VL Housekeeping Task", "VL Service Request",
		"VL Event Booking", "VL Rate Plan", "VL Property",
		"VL Floor", "VL Maintenance Request", "VL Guest Feedback",
	];

	page.doctype_field = page.add_field({
		fieldtype: "Select",
		fieldname: "explore_doctype",
		label: __("Entity Type"),
		options: DOCTYPES.join("\n"),
		default: "VL Reservation",
		change() {
			page.entity_field.df.options = page.doctype_field.get_value();
			page.entity_field.set_value("");
			page.entity_field.refresh();
		},
	});

	page.entity_field = page.add_field({
		fieldtype: "Link",
		fieldname: "explore_entity",
		label: __("Entity"),
		options: "VL Reservation",
		change() {
			const dt = page.doctype_field.get_value();
			const dn = page.entity_field.get_value();
			if (dt && dn) explorer.explore(dt, dn);
		},
	});

	page.depth_field = page.add_field({
		fieldtype: "Select",
		fieldname: "depth",
		label: __("Depth"),
		options: "1\n2\n3",
		default: "2",
	});

	page.set_primary_action(__("Explore"), () => {
		const dt = page.doctype_field.get_value();
		const dn = page.entity_field.get_value();
		if (dt && dn) explorer.explore(dt, dn);
		else frappe.show_alert({ message: __("Select an entity"), indicator: "orange" });
	}, "search");

	page.set_secondary_action(__("ERD View"), () => explorer.showERD(), "hierarchy");

	const explorer = new VelaraExplorer(page);
	await explorer.init();

	const params = frappe.utils.get_url_params();
	if (params.doctype && params.name) {
		page.doctype_field.set_value(params.doctype);
		setTimeout(() => {
			page.entity_field.df.options = params.doctype;
			page.entity_field.set_value(params.name);
			page.entity_field.refresh();
		}, 300);
	}
};

class VelaraExplorer {
	constructor(page) {
		this.page = page;
		this.$wrapper = $('<div class="vl-explorer fv-fx-page-enter"></div>').appendTo(page.main);
		this.$graph = $('<div class="vl-explorer-graph"></div>').appendTo(this.$wrapper);
		this.$stats = $('<div class="vl-explorer-stats fv-fx-glass"></div>').prependTo(this.$wrapper);
		this.engine = null;

		this.COLORS = {
			"VL Reservation": "#C9A84C",
			"VL Room": "#2563eb",
			"VL Guest": "#059669",
			"VL Folio": "#d97706",
			"VL Room Type": "#8b5cf6",
			"VL Housekeeping Task": "#0891b2",
			"VL Service Request": "#be123c",
			"VL Event Booking": "#7c3aed",
			"VL Rate Plan": "#16a34a",
			"VL Property": "#475569",
			"VL Floor": "#64748b",
			"VL Maintenance Request": "#dc2626",
			"VL Guest Feedback": "#ca8a04",
		};

		this.RELATIONS = {
			"VL Reservation": [
				{ link: "VL Room", via: "room", label: __("room"), reverse: true },
				{ link: "VL Guest", via: "guest", label: __("guest"), reverse: true },
				{ link: "VL Folio", via: "reservation", label: __("folios") },
				{ link: "VL Rate Plan", via: "rate_plan", label: __("rate plan"), reverse: true },
			],
			"VL Room": [
				{ link: "VL Reservation", via: "room", label: __("reservations") },
				{ link: "VL Room Type", via: "room_type", label: __("type"), reverse: true },
				{ link: "VL Floor", via: "floor", label: __("floor"), reverse: true },
				{ link: "VL Housekeeping Task", via: "room", label: __("HK tasks") },
				{ link: "VL Maintenance Request", via: "room", label: __("maintenance") },
			],
			"VL Guest": [
				{ link: "VL Reservation", via: "guest", label: __("reservations") },
				{ link: "VL Folio", via: "guest", label: __("folios") },
				{ link: "VL Guest Feedback", via: "guest", label: __("feedback") },
				{ link: "VL Service Request", via: "guest", label: __("requests") },
			],
			"VL Folio": [
				{ link: "VL Reservation", via: "reservation", label: __("reservation"), reverse: true },
				{ link: "VL Guest", via: "guest", label: __("guest"), reverse: true },
			],
			"VL Room Type": [
				{ link: "VL Room", via: "room_type", label: __("rooms") },
				{ link: "VL Rate Plan", via: "room_type", label: __("rate plans") },
			],
			"VL Event Booking": [
				{ link: "VL Guest", via: "guest", label: __("guest"), reverse: true },
				{ link: "VL Room", via: "venue", label: __("venue"), reverse: true },
			],
		};
	}

	async init() {
		this._addStyles();
		this._renderEmptyState();
	}

	async explore(doctype, name) {
		this.$graph.html(`<div class="text-center p-5"><div class="spinner-border text-primary"></div></div>`);
		this.$stats.empty();

		try {
			const doc = await frappe.xcall("frappe.client.get", { doctype, name });
			const nodes = [{ id: `${doctype}::${name}`, label: doc.name, doctype, color: this.COLORS[doctype] || "#C9A84C", central: true }];
			const edges = [];
			const visited = new Set([`${doctype}::${name}`]);
			const depth = parseInt(this.page.depth_field.get_value()) || 2;

			await this._expandNode(doctype, name, doc, nodes, edges, visited, depth);
			this._renderGraph(nodes, edges);
			this._renderStats(doctype, doc, nodes.length, edges.length);
		} catch (e) {
			this.$graph.html(`<div class="text-center p-5 text-muted">${__("Error")}: ${frappe.utils.escape_html(e.message || "")}</div>`);
		}
	}

	async _expandNode(doctype, name, doc, nodes, edges, visited, depthLeft) {
		if (depthLeft <= 0) return;
		const relations = this.RELATIONS[doctype] || [];

		for (const rel of relations) {
			try {
				let children;
				if (rel.reverse) {
					children = [{ name: doc[rel.via] }].filter(c => c.name);
				} else {
					children = await frappe.xcall("frappe.client.get_list", {
						doctype: rel.link,
						filters: { [rel.via]: name },
						fields: ["name"],
						limit_page_length: 15,
					});
				}

				for (const child of children) {
					const nodeId = `${rel.link}::${child.name}`;
					if (!visited.has(nodeId)) {
						visited.add(nodeId);
						nodes.push({
							id: nodeId, label: child.name, doctype: rel.link,
							color: this.COLORS[rel.link] || "#94a3b8",
						});
					}
					edges.push({ source: `${doctype}::${name}`, target: nodeId, label: rel.label });

					if (depthLeft > 1 && !rel.reverse) {
						const childDoc = await frappe.xcall("frappe.client.get", { doctype: rel.link, name: child.name });
						await this._expandNode(rel.link, child.name, childDoc, nodes, edges, visited, depthLeft - 1);
					}
				}
			} catch (_) { /* skip inaccessible */ }
		}
	}

	_renderGraph(nodes, edges) {
		this.$graph.empty().css({ height: "600px", position: "relative" });

		const renderVisual = () => {
			frappe.visual.engine().then(engine => {
				engine.init(this.$graph[0], {
					nodes: nodes.map(n => ({
						id: n.id, label: n.label,
						style: {
							background: n.color, color: "#fff",
							borderRadius: n.central ? "50%" : "8px",
							padding: n.central ? "16px 20px" : "8px 14px",
							fontSize: n.central ? "14px" : "12px",
							fontWeight: n.central ? "700" : "400",
							boxShadow: n.central ? `0 0 20px ${n.color}40` : "0 2px 8px rgba(0,0,0,0.1)",
						},
					})),
					edges: edges.map((e, i) => ({ id: `e${i}`, source: e.source, target: e.target, label: e.label })),
					layout: "elk-radial",
					onNodeClick: (id) => {
						const [dt, dn] = id.split("::");
						if (dt && dn) frappe.set_route("Form", dt, dn);
					},
					onNodeDblClick: (id) => {
						const [dt, dn] = id.split("::");
						if (dt && dn) {
							this.page.doctype_field.set_value(dt);
							setTimeout(() => {
								this.page.entity_field.df.options = dt;
								this.page.entity_field.set_value(dn);
							}, 100);
						}
					},
				});
			}).catch(() => this._renderFallback(nodes));
		};

		if (frappe.visual && frappe.visual.engine) {
			renderVisual();
		} else {
			frappe.require("frappe_visual.bundle.js", () => {
				if (frappe.visual && frappe.visual.engine) renderVisual();
				else this._renderFallback(nodes);
			});
		}
	}

	_renderFallback(nodes) {
		const html = nodes.map(n => `
			<div class="fv-fx-hover-lift" style="display:inline-block;padding:10px 16px;margin:6px;
				border-radius:8px;background:${n.color};color:#fff;cursor:pointer;font-size:12px;
				${n.central ? "font-weight:700;font-size:14px;" : ""}"
				onclick="frappe.set_route('Form','${n.doctype}','${n.label}')">
				${frappe.utils.escape_html(n.label)}
				<small style="opacity:0.7;display:block">${frappe.utils.escape_html(n.doctype)}</small>
			</div>
		`).join("");
		this.$graph.html(`<div class="p-4 text-center">${html}</div>`);
	}

	_renderStats(doctype, doc, nodeCount, edgeCount) {
		const title = doc.guest_name || doc.room_name || doc.name;
		this.$stats.html(`
			<div style="display:flex;gap:24px;align-items:center;padding:16px 24px;flex-wrap:wrap">
				<div>
					<div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase">${__("Entity")}</div>
					<div style="font-size:1.1rem;font-weight:700">${frappe.utils.escape_html(title)}</div>
					<div style="font-size:0.8rem;color:var(--text-light)">${frappe.utils.escape_html(doctype)}</div>
				</div>
				<div style="margin-inline-start:auto;display:flex;gap:20px">
					<div class="text-center">
						<div style="font-size:1.5rem;font-weight:800;color:#C9A84C">${nodeCount}</div>
						<div style="font-size:0.7rem;color:var(--text-muted)">${__("Nodes")}</div>
					</div>
					<div class="text-center">
						<div style="font-size:1.5rem;font-weight:800;color:var(--orange-500)">${edgeCount}</div>
						<div style="font-size:0.7rem;color:var(--text-muted)">${__("Links")}</div>
					</div>
				</div>
			</div>
		`);
	}

	showERD() {
		const dlg = new frappe.ui.Dialog({
			title: __("Velara ERD — Hotel Entity Relationships"),
			size: "extra-large",
			fields: [{ fieldtype: "HTML", fieldname: "erd_area" }],
		});

		const erdData = {
			nodes: Object.keys(this.COLORS).map(dt => ({
				id: dt, label: dt.replace("VL ", ""),
				style: { background: this.COLORS[dt], color: "#fff", borderRadius: "8px", padding: "10px 16px" },
			})),
			edges: [],
		};

		for (const [dt, rels] of Object.entries(this.RELATIONS)) {
			for (const rel of rels) {
				if (!rel.reverse) {
					erdData.edges.push({ id: `${dt}-${rel.link}`, source: dt, target: rel.link, label: rel.label });
				}
			}
		}

		dlg.show();
		const area = dlg.fields_dict.erd_area.$wrapper[0];
		area.style.height = "500px";

		if (frappe.visual && frappe.visual.engine) {
			frappe.visual.engine().then(e => e.init(area, { ...erdData, layout: "elk-layered" }));
		} else {
			area.innerHTML = `<div class="p-4">${erdData.nodes.map(n =>
				`<span style="display:inline-block;padding:6px 12px;margin:4px;border-radius:6px;background:${n.style.background};color:#fff;font-size:12px">${n.label}</span>`
			).join("")}</div>`;
		}
	}

	_renderEmptyState() {
		this.$graph.html(`
			<div style="text-align:center;padding:80px 20px">
				<div style="font-size:3rem;margin-bottom:16px">🏨</div>
				<h3 style="color:var(--text-muted)">${__("Select a hotel entity to explore")}</h3>
				<p style="color:var(--text-light);max-width:400px;margin:8px auto">
					${__("Choose a DocType and entity above, then click Explore to visualize all relationships.")}
				</p>
			</div>
		`);
	}

	_addStyles() {
		if (document.getElementById("vl-explorer-styles")) return;
		const style = document.createElement("style");
		style.id = "vl-explorer-styles";
		style.textContent = `
			.vl-explorer { min-height: 700px; }
			.vl-explorer-stats {
				border-radius: 12px; margin-bottom: 16px;
				background: var(--card-bg); border: 1px solid var(--border-color);
			}
			.vl-explorer-graph {
				border-radius: 12px; background: var(--card-bg);
				border: 1px solid var(--border-color); overflow: hidden;
			}
		`;
		document.head.appendChild(style);
	}
}
