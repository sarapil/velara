// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.pages["velara-dashboard"].on_page_load = function (wrapper) {
frappe.velara_dashboard = new VelaraDashboard(wrapper);
};

frappe.pages["velara-dashboard"].on_page_show = function () {
frappe.velara_dashboard && frappe.velara_dashboard.refresh();
};

class VelaraDashboard {
constructor(wrapper) {
this.wrapper = wrapper;
this.page = frappe.ui.make_app_page({
parent: wrapper,
title: __("Hotel Dashboard"),
single_column: true,
});

frappe.breadcrumbs.add("Velara", "velara-dashboard");
this.setup_actions();
this.render_layout();
this.load_data();
}

setup_actions() {
this.page.set_primary_action(__("Refresh"), () => this.load_data(), "refresh");

this.page.add_inner_button(__("Night Audit"), () => {
frappe.set_route("List", "VL Night Audit");
});
this.page.add_inner_button(__("Reservations"), () => {
frappe.set_route("List", "VL Reservation");
});
}

render_layout() {
this.page.main.html(`
<div class="velara-dashboard">
<div class="vl-metrics-row"></div>
<div class="vl-charts-row">
<div class="vl-chart-card vl-occupancy-chart">
<h5>${__("Occupancy Overview")}</h5>
<div class="chart-container"></div>
</div>
<div class="vl-chart-card vl-arrivals-chart">
<h5>${__("Today's Activity")}</h5>
<div class="chart-container"></div>
</div>
</div>
<div class="vl-tables-row">
<div class="vl-table-card vl-arrivals-table">
<h5>${__("Expected Arrivals")}</h5>
<div class="table-container"></div>
</div>
<div class="vl-table-card vl-departures-table">
<h5>${__("Expected Departures")}</h5>
<div class="table-container"></div>
</div>
</div>
<div class="vl-hk-summary">
<h5>${__("Housekeeping Status")}</h5>
<div class="hk-container"></div>
</div>
</div>
`);
}

load_data() {
frappe.call({
method: "velara.api.dashboard.get_dashboard_data",
freeze: true,
freeze_message: __("Loading dashboard..."),
callback: (r) => {
if (r.message) {
this.data = r.message;
this.render_metrics();
this.render_arrivals_table();
this.render_departures_table();
this.render_hk_summary();
}
},
});
}

render_metrics() {
const d = this.data;
const metrics = [
{ label: __("Total Rooms"), value: d.total_rooms || 0, icon: "door", color: "blue" },
{ label: __("Occupied"), value: d.occupied || 0, icon: "bed", color: "green" },
{ label: __("Available"), value: d.available || 0, icon: "check", color: "cyan" },
{ label: __("Occupancy %"), value: `${d.occupancy_pct || 0}%`, icon: "chart-bar", color: "orange" },
{ label: __("Arrivals Today"), value: d.arrivals_today || 0, icon: "login", color: "purple" },
{ label: __("Departures Today"), value: d.departures_today || 0, icon: "logout", color: "red" },
{ label: __("Revenue Today"), value: frappe.format(d.revenue_today || 0, { fieldtype: "Currency" }), icon: "currency-dollar", color: "green" },
{ label: __("ADR"), value: frappe.format(d.adr || 0, { fieldtype: "Currency" }), icon: "trending-up", color: "blue" },
];

const html = metrics
.map(
(m) => `
<div class="vl-metric-card vl-metric-${m.color}">
<div class="metric-icon">${frappe.visual?.icons?.render(m.icon, { size: "md" }) || ""}</div>
<div class="metric-value">${m.value}</div>
<div class="metric-label">${m.label}</div>
</div>`
)
.join("");

this.page.main.find(".vl-metrics-row").html(html);
}

render_arrivals_table() {
const arrivals = this.data.arrivals || [];
const html = arrivals.length
? `<table class="table table-sm">
<thead><tr>
<th>${__("Guest")}</th><th>${__("Room")}</th>
<th>${__("Room Type")}</th><th>${__("Status")}</th>
</tr></thead>
<tbody>${arrivals
.map(
(a) => `<tr>
<td><a href="/app/vl-guest/${a.guest}">${a.guest_name || a.guest}</a></td>
<td>${a.room || "-"}</td>
<td>${a.room_type || "-"}</td>
<td><span class="indicator-pill ${a.status === "Checked In" ? "green" : "orange"}">${a.status}</span></td>
</tr>`
)
.join("")}</tbody></table>`
: `<p class="text-muted">${__("No arrivals today")}</p>`;
this.page.main.find(".vl-arrivals-table .table-container").html(html);
}

render_departures_table() {
const departures = this.data.departures || [];
const html = departures.length
? `<table class="table table-sm">
<thead><tr>
<th>${__("Guest")}</th><th>${__("Room")}</th>
<th>${__("Folio Balance")}</th><th>${__("Status")}</th>
</tr></thead>
<tbody>${departures
.map(
(d) => `<tr>
<td><a href="/app/vl-guest/${d.guest}">${d.guest_name || d.guest}</a></td>
<td>${d.room || "-"}</td>
<td>${frappe.format(d.folio_balance || 0, { fieldtype: "Currency" })}</td>
<td><span class="indicator-pill ${d.status === "Checked Out" ? "green" : "blue"}">${d.status}</span></td>
</tr>`
)
.join("")}</tbody></table>`
: `<p class="text-muted">${__("No departures today")}</p>`;
this.page.main.find(".vl-departures-table .table-container").html(html);
}

render_hk_summary() {
const hk = this.data.housekeeping || {};
const statuses = [
{ label: __("Clean"), count: hk.clean || 0, color: "green" },
{ label: __("Dirty"), count: hk.dirty || 0, color: "red" },
{ label: __("In Progress"), count: hk.in_progress || 0, color: "orange" },
{ label: __("Inspected"), count: hk.inspected || 0, color: "blue" },
{ label: __("Out of Order"), count: hk.out_of_order || 0, color: "grey" },
];
const html = statuses
.map(
(s) => `<div class="vl-hk-pill">
<span class="indicator-pill ${s.color}">${s.count}</span>
<span class="hk-label">${s.label}</span>
</div>`
)
.join("");
this.page.main.find(".vl-hk-summary .hk-container").html(html);
}

refresh() {
this.load_data();
}
}
