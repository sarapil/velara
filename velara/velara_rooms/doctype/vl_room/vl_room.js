// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.ui.form.on("VL Room", {
	refresh(frm) {
		// Status badges
		let colors = {
			"Available": "green", "Occupied": "red", "Reserved": "blue",
			"Dirty": "orange", "Clean": "green", "Inspected": "darkgrey",
			"Out of Order": "red", "Out of Service": "grey"
		};
		frm.page.set_indicator(frm.doc.room_status, colors[frm.doc.room_status] || "grey");

		// Quick status change buttons
		if (!frm.is_new()) {
			if (frm.doc.room_status === "Dirty") {
				frm.add_custom_button(__("Mark Clean"), () => {
					frm.call("change_status", { new_status: "Clean" }).then(() => frm.reload_doc());
				});
			}
			if (frm.doc.room_status === "Clean") {
				frm.add_custom_button(__("Mark Inspected"), () => {
					frm.call("change_status", { new_status: "Inspected" }).then(() => frm.reload_doc());
				});
			}
			if (!["Out of Order", "Out of Service"].includes(frm.doc.room_status)) {
				frm.add_custom_button(__("Block Room"), () => {
					frappe.new_doc("VL Room Block", { room: frm.doc.name });
				}, __("Actions"));
			}
			if (["Inspected", "Clean"].includes(frm.doc.room_status)) {
				frm.add_custom_button(__("Mark Available"), () => {
					frm.call("change_status", { new_status: "Available" }).then(() => frm.reload_doc());
				});
			}
		}

		// Current guest info
		if (frm.doc.current_guest) {
			frm.dashboard.add_indicator(__("Guest: {0}", [frm.doc.current_guest]), "blue");
		}
		if (frm.doc.current_reservation) {
			frm.dashboard.add_indicator(__("Res: {0}", [frm.doc.current_reservation]), "green");
		}

		// 3D Floor Plan button
		if (!frm.is_new()) {
			frm.add_custom_button(__("3D Floor Plan"), async () => {
				const d = new frappe.ui.Dialog({
					title: __("Hotel Floor Plan — Floor {0}", [frm.doc.floor_number || ""]),
					size: "extra-large",
				});
				d.body.style.height = "600px";
				d.show();

				frappe.require("/assets/velara/js/3d_engine/velara_3d.js", async () => {
					await frappe.velara.floorPlan.createDashboard(d.body, {
						property: frm.doc.property,
						floor: frm.doc.floor_number,
					});
				});
			}, __("View"));

			// Visual room dashboard
			render_vl_room_visual(frm);
		}
	}
});

function render_vl_room_visual(frm) {
	const sc = {
		Available: "var(--green-500)", Occupied: "var(--red-500)", Reserved: "var(--blue-500)",
		Dirty: "var(--orange-500)", Clean: "var(--green-400)", Inspected: "var(--text-muted)",
		"Out of Order": "var(--red-600)", "Out of Service": "var(--text-muted)",
	};
	const color = sc[frm.doc.room_status] || "var(--text-muted)";

	const wrapper = frm.dashboard.add_section("", __("Room Info"));
	$(wrapper).html(`
		<div class="vl-room-visual fv-fx-page-enter" style="padding:12px 0;">
			<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:10px;">
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:20px;font-weight:700;color:${color};">${__(frm.doc.room_status || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Status")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${frappe.utils.escape_html(frm.doc.room_type || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Type")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:24px;font-weight:700;color:var(--primary);">${frm.doc.floor_number || "—"}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Floor")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${frappe.utils.escape_html(frm.doc.current_guest || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Current Guest")}</div>
				</div>
			</div>
		</div>
	`);
}
