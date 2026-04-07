// Copyright (c) 2024, Moataz M Hassan (Arkan Lab)
// Developer Website: https://arkan.it.com
// License: MIT
// For license information, please see license.txt

frappe.ui.form.on("VL Reservation", {
	refresh(frm) {
		// Status indicator
		frm.page.set_indicator(frm.doc.status, {
			"Draft": "orange", "Tentative": "blue", "Confirmed": "green",
			"Guaranteed": "purple", "Checked In": "green", "Checked Out": "darkgrey",
			"Cancelled": "red", "No Show": "red"
		}[frm.doc.status] || "grey");

		if (frm.doc.docstatus === 1) {
			// Assign Room
			if (!frm.doc.room && ["Confirmed", "Guaranteed"].includes(frm.doc.status)) {
				frm.add_custom_button(__("Assign Room"), () => {
					frappe.call({
						method: "velara.api.room.get_available_rooms",
						args: {
							room_type: frm.doc.room_type,
							check_in: frm.doc.check_in_date,
							check_out: frm.doc.check_out_date
						},
						callback(r) {
							if (r.message && r.message.length) {
								let d = new frappe.ui.Dialog({
									title: __("Select Room"),
									fields: [{
										fieldname: "room", fieldtype: "Select",
										label: __("Room"),
										options: r.message.map(rm => rm.name).join("\n"),
										reqd: 1
									}],
									primary_action(values) {
										frm.call("assign_room", { room: values.room })
											.then(() => { d.hide(); frm.reload_doc(); });
									}
								});
								d.show();
							} else {
								frappe.msgprint(__("No rooms available for the selected dates"));
							}
						}
					});
				}, __("Actions"));
			}

			// Check In button
			if (["Confirmed", "Guaranteed"].includes(frm.doc.status) && frm.doc.room) {
				frm.add_custom_button(__("Check In"), () => {
					frappe.new_doc("VL Check In", { reservation: frm.doc.name });
				}, __("Actions"));
			}

			// Create Folio
			if (!frm.doc.folio && frm.doc.status === "Checked In") {
				frm.add_custom_button(__("Create Folio"), () => {
					frm.call("create_folio").then(() => frm.reload_doc());
				}, __("Actions"));
			}

			// Check Out
			if (frm.doc.status === "Checked In") {
				frm.add_custom_button(__("Check Out"), () => {
					frappe.new_doc("VL Check Out", { reservation: frm.doc.name });
				}, __("Actions"));
			}

			// Cancel / No Show
			if (["Confirmed", "Guaranteed", "Tentative"].includes(frm.doc.status)) {
				frm.add_custom_button(__("Cancel"), () => {
					frappe.confirm(__("Are you sure you want to cancel this reservation?"), () => {
						frappe.xcall("frappe.client.cancel", { doctype: "VL Reservation", name: frm.doc.name })
							.then(() => frm.reload_doc());
					});
				}, __("Actions"));

				frm.add_custom_button(__("Mark No Show"), () => {
					frappe.call({
						method: "frappe.client.amend",
						args: { doctype: "VL Reservation", name: frm.doc.name },
						callback() { frm.reload_doc(); }
					});
				}, __("Actions"));
			}
		}

		// Dashboard
		if (!frm.is_new()) {
			frm.dashboard.add_indicator(
				__("Nights: {0}", [frm.doc.nights || 0]), "blue"
			);
			if (frm.doc.folio) {
				frm.dashboard.add_indicator(
					__("Folio: {0}", [frm.doc.folio]), "green"
				);
			}

			// Visual reservation dashboard
			render_vl_reservation_visual(frm);
		}
	},

	check_in_date(frm) { calculate_nights(frm); },
	check_out_date(frm) { calculate_nights(frm); },

	room_type(frm) {
		if (frm.doc.room_type && !frm.doc.room_rate) {
			frappe.db.get_value("VL Room Type", frm.doc.room_type, "default_rate")
				.then(r => { if (r.message) frm.set_value("room_rate", r.message.default_rate); });
		}
	},

	rate_plan(frm) {
		if (frm.doc.rate_plan) {
			frappe.db.get_value("VL Rate Plan", frm.doc.rate_plan, "base_rate")
				.then(r => { if (r.message) frm.set_value("room_rate", r.message.base_rate); });
		}
	},

	room_rate(frm) { calculate_charges(frm); },
	discount_percent(frm) { calculate_charges(frm); },
});

function calculate_nights(frm) {
	if (frm.doc.check_in_date && frm.doc.check_out_date) {
		let nights = frappe.datetime.get_diff(frm.doc.check_out_date, frm.doc.check_in_date);
		frm.set_value("nights", nights > 0 ? nights : 0);
		calculate_charges(frm);
	}
}

function calculate_charges(frm) {
	let rate = flt(frm.doc.room_rate);
	let nights = cint(frm.doc.nights) || 1;
	let total = rate * nights;
	frm.set_value("total_room_charges", total);

	let disc = flt(frm.doc.discount_percent);
	frm.set_value("net_total", disc > 0 ? total * (1 - disc / 100) : total);
}

function render_vl_reservation_visual(frm) {
	const ci = frm.doc.check_in_date;
	const co = frm.doc.check_out_date;
	const days_until = ci ? frappe.datetime.get_diff(ci, frappe.datetime.get_today()) : null;

	let arrival_text = "";
	if (days_until !== null) {
		if (days_until < 0) arrival_text = __("{0} days ago", [Math.abs(days_until)]);
		else if (days_until === 0) arrival_text = __("Today");
		else arrival_text = __("In {0} days", [days_until]);
	}

	const status_colors = {
		Draft: "#9CA3AF", Tentative: "#60A5FA", Confirmed: "#34D399",
		Guaranteed: "#A78BFA", "Checked In": "#10B981", "Checked Out": "#6B7280",
		Cancelled: "#EF4444", "No Show": "#F87171",
	};
	const sc = status_colors[frm.doc.status] || "#9CA3AF";

	const wrapper = frm.dashboard.add_section("", __("Stay Overview"));
	$(wrapper).html(`
		<div class="vl-res-visual fv-fx-page-enter" style="padding:12px 0;">
			<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;">
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:28px;font-weight:700;color:${sc};">${__(frm.doc.status || "—")}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Status")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:28px;font-weight:700;color:var(--primary);">${frm.doc.nights || 0}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Nights")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:20px;font-weight:700;color:var(--green-500);">
						${format_currency(frm.doc.net_total || frm.doc.total_room_charges || 0)}
					</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Net Total")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${frm.doc.room || "—"}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Room")}</div>
				</div>
				<div class="fv-fx-glass fv-fx-hover-lift" style="padding:14px;border-radius:10px;text-align:center;">
					<div style="font-size:16px;font-weight:600;">${arrival_text || "—"}</div>
					<div style="font-size:11px;color:var(--text-muted);">${__("Arrival")}</div>
				</div>
			</div>
		</div>
	`);
}
