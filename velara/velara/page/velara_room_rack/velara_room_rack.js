// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.pages["velara-room-rack"].on_page_load = function (wrapper) {
frappe.velara_room_rack = new VelaraRoomRack(wrapper);
};

frappe.pages["velara-room-rack"].on_page_show = function () {
frappe.velara_room_rack && frappe.velara_room_rack.refresh();
};

class VelaraRoomRack {
constructor(wrapper) {
this.wrapper = wrapper;
this.page = frappe.ui.make_app_page({
parent: wrapper,
title: __("Room Rack"),
single_column: true,
});

frappe.breadcrumbs.add("Velara", "velara-room-rack");
this.filters = {};
this.setup_actions();
this.render_layout();
this.load_data();
}

setup_actions() {
this.page.set_primary_action(__("Refresh"), () => this.load_data(), "refresh");

// Floor filter
this.page.add_field({
fieldname: "floor",
label: __("Floor"),
fieldtype: "Link",
options: "VL Floor",
change: () => this.apply_filters(),
});

// Room status filter
this.page.add_field({
fieldname: "room_status",
label: __("Status"),
fieldtype: "Select",
options: "\nAvailable\nOccupied\nReserved\nOut of Order\nDirty",
change: () => this.apply_filters(),
});

// Room type filter
this.page.add_field({
fieldname: "room_type",
label: __("Room Type"),
fieldtype: "Link",
options: "VL Room Type",
change: () => this.apply_filters(),
});
}

render_layout() {
this.page.main.html(`
<div class="velara-room-rack">
<div class="rack-legend"></div>
<div class="rack-grid"></div>
</div>
`);

// Render legend
const legend_items = [
{ label: __("Available"), color: "#2ecc71" },
{ label: __("Occupied"), color: "#3498db" },
{ label: __("Reserved"), color: "#f39c12" },
{ label: __("Dirty"), color: "#e74c3c" },
{ label: __("Out of Order"), color: "#95a5a6" },
];
const legend_html = legend_items
.map((l) => `<div class="legend-item"><span class="legend-dot" style="background:${l.color}"></span>${l.label}</div>`)
.join("");
this.page.main.find(".rack-legend").html(legend_html);
}

load_data() {
frappe.call({
method: "velara.api.room.get_floor_map",
freeze: true,
callback: (r) => {
if (r.message) {
this.rooms = r.message.rooms || [];
this.floors = r.message.floors || [];
this.render_rack();
}
},
});
}

apply_filters() {
const floor = this.page.fields_dict.floor?.get_value();
const status = this.page.fields_dict.room_status?.get_value();
const room_type = this.page.fields_dict.room_type?.get_value();

this.page.main.find(".rack-floor").show();
this.page.main.find(".room-card").show();

if (floor) {
this.page.main.find(`.rack-floor:not([data-floor="${floor}"])`).hide();
}

this.page.main.find(".room-card").each(function () {
const $card = $(this);
let show = true;
if (status && $card.data("status") !== status) show = false;
if (room_type && $card.data("room-type") !== room_type) show = false;
if (!show) $card.hide();
});
}

render_rack() {
const grid = this.page.main.find(".rack-grid");

if (!this.floors.length) {
grid.html(`<p class="text-muted text-center">${__("No rooms found")}</p>`);
return;
}

const status_colors = {
Available: "#2ecc71",
Occupied: "#3498db",
Reserved: "#f39c12",
Dirty: "#e74c3c",
"Out of Order": "#95a5a6",
};

let html = "";
for (const floor of this.floors) {
const floor_rooms = this.rooms.filter((r) => r.floor === floor.name);
if (!floor_rooms.length) continue;

html += `<div class="rack-floor" data-floor="${floor.name}">
<div class="floor-header">
<strong>${floor.floor_name || floor.name}</strong>
<span class="text-muted">(${floor_rooms.length} ${__("rooms")})</span>
</div>
<div class="floor-rooms">`;

for (const room of floor_rooms) {
const color = status_colors[room.room_status] || "#95a5a6";
const guest_info = room.current_guest
? `<div class="room-guest">${frappe.utils.escape_html(room.guest_name || room.current_guest)}</div>`
: "";

html += `<div class="room-card"
data-room="${room.name}"
data-status="${room.room_status}"
data-room-type="${room.room_type}"
style="border-left: 4px solid ${color};"
onclick="frappe.set_route('Form', 'VL Room', '${room.name}')">
<div class="room-number">${room.room_number}</div>
<div class="room-type-label">${room.room_type}</div>
<div class="room-status" style="color:${color}">${__(room.room_status)}</div>
${guest_info}
</div>`;
}

html += `</div></div>`;
}

grid.html(html);
}

refresh() {
this.load_data();
}
}
