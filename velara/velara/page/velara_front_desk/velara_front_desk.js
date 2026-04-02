frappe.pages["velara-front-desk"].on_page_load = function (wrapper) {
frappe.velara_front_desk = new VelaraFrontDesk(wrapper);
};

frappe.pages["velara-front-desk"].on_page_show = function () {
frappe.velara_front_desk && frappe.velara_front_desk.refresh();
};

class VelaraFrontDesk {
constructor(wrapper) {
this.wrapper = wrapper;
this.page = frappe.ui.make_app_page({
parent: wrapper,
title: __("Front Desk"),
single_column: true,
});

frappe.breadcrumbs.add("Velara", "velara-front-desk");
this.setup_actions();
this.render_layout();
this.load_data();
}

setup_actions() {
this.page.set_primary_action(__("Refresh"), () => this.load_data(), "refresh");

this.page.add_inner_button(__("New Reservation"), () => {
frappe.new_doc("VL Reservation");
});
this.page.add_inner_button(__("New Walk-In"), () => {
this.walk_in_dialog();
});
this.page.add_inner_button(__("Guest Search"), () => {
this.guest_search_dialog();
});
}

render_layout() {
this.page.main.html(`
<div class="velara-front-desk">
<div class="fd-quick-stats"></div>
<div class="fd-sections">
<div class="fd-section fd-pending-arrivals">
<h5>${__("Pending Arrivals")}</h5>
<div class="section-content"></div>
</div>
<div class="fd-section fd-pending-departures">
<h5>${__("Pending Departures")}</h5>
<div class="section-content"></div>
</div>
</div>
<div class="fd-section fd-in-house">
<h5>${__("In-House Guests")}</h5>
<div class="section-content"></div>
</div>
</div>
`);
}

load_data() {
frappe.call({
method: "velara.api.front_desk.get_front_desk_data",
freeze: true,
callback: (r) => {
if (r.message) {
this.data = r.message;
this.render_quick_stats();
this.render_pending_arrivals();
this.render_pending_departures();
this.render_in_house();
}
},
});
}

render_quick_stats() {
const d = this.data;
const stats = [
{ label: __("Arrivals"), value: d.arrivals_count || 0, icon: "login", color: "green" },
{ label: __("Departures"), value: d.departures_count || 0, icon: "logout", color: "orange" },
{ label: __("In-House"), value: d.in_house_count || 0, icon: "home", color: "blue" },
{ label: __("Available Rooms"), value: d.available_rooms || 0, icon: "door", color: "cyan" },
];

const html = stats
.map(
(s) => `<div class="fd-stat fd-stat-${s.color}">
<div class="stat-value">${s.value}</div>
<div class="stat-label">${s.label}</div>
</div>`
)
.join("");
this.page.main.find(".fd-quick-stats").html(html);
}

render_pending_arrivals() {
const arrivals = this.data.pending_arrivals || [];
const html = arrivals.length
? arrivals
.map(
(a) => `<div class="fd-guest-row" data-reservation="${a.name}">
<div class="guest-info">
<strong>${a.guest_name || a.guest}</strong>
<span class="text-muted">${a.room_type || ""}</span>
</div>
<div class="guest-room">${a.room || __("Unassigned")}</div>
<button class="btn btn-xs btn-primary" onclick="frappe.velara_front_desk.quick_check_in('${a.name}')">${__("Check In")}</button>
</div>`
)
.join("")
: `<p class="text-muted">${__("No pending arrivals")}</p>`;
this.page.main.find(".fd-pending-arrivals .section-content").html(html);
}

render_pending_departures() {
const departures = this.data.pending_departures || [];
const html = departures.length
? departures
.map(
(d) => `<div class="fd-guest-row" data-reservation="${d.name}">
<div class="guest-info">
<strong>${d.guest_name || d.guest}</strong>
<span class="text-muted">${__("Room")} ${d.room || "-"}</span>
</div>
<div class="guest-balance">${frappe.format(d.balance || 0, { fieldtype: "Currency" })}</div>
<button class="btn btn-xs btn-warning" onclick="frappe.velara_front_desk.quick_check_out('${d.name}')">${__("Check Out")}</button>
</div>`
)
.join("")
: `<p class="text-muted">${__("No pending departures")}</p>`;
this.page.main.find(".fd-pending-departures .section-content").html(html);
}

render_in_house() {
const guests = this.data.in_house || [];
const html = guests.length
? `<table class="table table-sm">
<thead><tr>
<th>${__("Guest")}</th><th>${__("Room")}</th>
<th>${__("Check In")}</th><th>${__("Check Out")}</th>
<th>${__("Nights")}</th><th>${__("Folio")}</th>
</tr></thead>
<tbody>${guests
.map(
(g) => `<tr>
<td><a href="/app/vl-guest/${g.guest}">${g.guest_name || g.guest}</a></td>
<td>${g.room || "-"}</td>
<td>${frappe.format(g.check_in_date, { fieldtype: "Date" })}</td>
<td>${frappe.format(g.check_out_date, { fieldtype: "Date" })}</td>
<td>${g.nights || "-"}</td>
<td>${g.folio ? `<a href="/app/vl-folio/${g.folio}">${g.folio}</a>` : "-"}</td>
</tr>`
)
.join("")}</tbody></table>`
: `<p class="text-muted">${__("No in-house guests")}</p>`;
this.page.main.find(".fd-in-house .section-content").html(html);
}

quick_check_in(reservation) {
frappe.new_doc("VL Check In", { reservation: reservation });
}

quick_check_out(reservation) {
frappe.new_doc("VL Check Out", { reservation: reservation });
}

walk_in_dialog() {
const d = new frappe.ui.Dialog({
title: __("Walk-In Guest"),
fields: [
{ fieldname: "first_name", label: __("First Name"), fieldtype: "Data", reqd: 1 },
{ fieldname: "last_name", label: __("Last Name"), fieldtype: "Data" },
{ fieldname: "mobile", label: __("Mobile"), fieldtype: "Data" },
{ fieldname: "email", label: __("Email"), fieldtype: "Data" },
{ fieldname: "id_type", label: __("ID Type"), fieldtype: "Select",
  options: "National ID\nPassport\nDriving License" },
{ fieldname: "id_number", label: __("ID Number"), fieldtype: "Data" },
{ fieldname: "sb1", fieldtype: "Section Break", label: __("Room") },
{ fieldname: "room_type", label: __("Room Type"), fieldtype: "Link",
  options: "VL Room Type", reqd: 1 },
{ fieldname: "nights", label: __("Nights"), fieldtype: "Int", default: 1 },
],
primary_action_label: __("Create"),
primary_action: (values) => {
frappe.call({
method: "velara.api.front_desk.walk_in_check_in",
args: values,
callback: (r) => {
if (r.message) {
d.hide();
frappe.set_route("Form", "VL Reservation", r.message);
}
},
});
},
});
d.show();
}

guest_search_dialog() {
const d = new frappe.ui.Dialog({
title: __("Guest Search"),
fields: [
{ fieldname: "search", label: __("Name, Email or Phone"), fieldtype: "Data", reqd: 1 },
],
primary_action_label: __("Search"),
primary_action: (values) => {
frappe.call({
method: "velara.api.front_desk.search_guest",
args: { query: values.search },
callback: (r) => {
const guests = r.message || [];
if (guests.length === 1) {
d.hide();
frappe.set_route("Form", "VL Guest", guests[0].name);
} else if (guests.length > 1) {
frappe.msgprint({
title: __("Results"),
message: guests
.map((g) => `<a href="/app/vl-guest/${g.name}">${g.guest_name} (${g.email || g.mobile || ""})</a>`)
.join("<br>"),
});
d.hide();
} else {
frappe.msgprint(__("No guests found"));
}
},
});
},
});
d.show();
}

refresh() {
this.load_data();
}
}
