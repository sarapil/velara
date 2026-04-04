app_name = "velara"
app_title = "VELARA"
app_publisher = "ARKAN"
app_description = "Hotel & Hospitality Management System - نظام إدارة الفنادق والضيافة"
app_email = "moataz.sarapil@gmail.com"
app_license = "mit"
app_icon = "/assets/velara/images/velara-logo.svg"
app_color = "#C9A84C"
app_logo_url = "/assets/velara/images/velara-logo.svg"

# Required Apps
# ------------------
required_apps = ["frappe", "erpnext", "hrms", "frappe_visual", "arkan_help"]

# Apps Screen
# ------------------
add_to_apps_screen = [
	{
		"name": "velara",
		"logo": "/assets/velara/icons/desktop_icons/solid/velara.svg",
		"title": "Velara",
		"route": "/app/velara",
		"has_permission": "velara.api.permissions.has_app_permission"
	}
]

# Includes in <head>
# ------------------
app_include_css = [
        "/assets/velara/css/velara-theme.css",
	"/assets/velara/css/velara-variables.css"
]

app_include_js = [
	"/assets/velara/js/velara_boot.js"
]

# DocType JS Extensions (ERPNext)
# ------------------
doctype_js = {
	"Customer": "public/js/extensions/customer.js",
	"Sales Invoice": "public/js/extensions/sales_invoice.js",
	"Payment Entry": "public/js/extensions/payment_entry.js",
	"Employee": "public/js/extensions/employee.js",
	"Stock Entry": "public/js/extensions/stock_entry.js",
	"POS Invoice": "public/js/extensions/pos_invoice.js",
	"Asset": "public/js/extensions/asset.js",
}

# Home Pages
# ------------------
role_home_page = {
	"Velara Admin": "velara",
	"Velara General Manager": "velara",
	"Velara Front Desk Manager": "velara",
	"Velara Front Desk Agent": "velara",
	"Velara Housekeeping Manager": "velara",
	"Velara Housekeeper": "velara",
	"Velara Revenue Manager": "velara",
	"Velara FnB Manager": "velara",
	"Velara Concierge": "velara",
	"Velara Maintenance Tech": "velara",
	"Velara Events Coordinator": "velara",
	"Velara Spa Manager": "velara",
	"Velara Night Auditor": "velara",
	"Velara Viewer": "velara",
}

# Installation
# ------------------
before_install = "velara.install.before_install"
after_install = "velara.install.after_install"

after_migrate = ["velara.seed.seed_data"]

# Uninstallation
# ------------------
before_uninstall = "velara.uninstall.before_uninstall"
after_uninstall = "velara.uninstall.after_uninstall"

# Website Context
# ------------------
website_context = {
	"favicon": "/assets/velara/images/velara-favicon.svg",
	"splash_image": "/assets/velara/images/velara-splash.svg",
}

# Boot Session
# ------------------
boot_session = "velara.boot.boot_session"

# Notification Config
# ------------------
notification_config = "velara.notifications.get_notification_config"

# Document Events
# ---------------
doc_events = {
	"Customer": {
		"after_insert": "velara.events.customer_events.after_insert",
		"on_update": "velara.events.customer_events.on_update",
	},
	"Sales Invoice": {
		"on_submit": "velara.events.sales_invoice_events.on_submit",
		"on_cancel": "velara.events.sales_invoice_events.on_cancel",
	},
	"Payment Entry": {
		"on_submit": "velara.events.payment_events.on_submit",
		"on_cancel": "velara.events.payment_events.on_cancel",
	},
	"Stock Entry": {
		"validate": "velara.events.stock_events.on_validate",
		"on_submit": "velara.events.stock_events.on_submit",
	},
	"POS Invoice": {
		"on_submit": "velara.events.pos_events.on_submit",
	},
	"Employee": {
		"on_update": "velara.events.employee_events.on_update",
	},
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"cron": {
		"0 2 * * *": [
			"velara.tasks.run_night_audit",
		],
		"*/10 * * * *": [
			"velara.tasks.update_room_statuses",
		],
		"*/30 * * * *": [
			"velara.tasks.check_reservation_deadlines",
		],
	},
	"daily": [
		"velara.tasks.send_arrival_list",
		"velara.tasks.send_departure_list",
		"velara.tasks.check_maintenance_schedules",
		"velara.tasks.auto_assign_housekeeping",
		"velara.tasks.process_loyalty_points",
	],
	"hourly": [
		"velara.tasks.sync_channel_rates",
		"velara.tasks.update_occupancy_forecast",
		"velara.tasks.check_folio_credit_limits",
	],
	"weekly": [
		"velara.tasks.generate_weekly_revenue_report",
		"velara.tasks.check_preventive_maintenance_due",
		"velara.tasks.send_guest_feedback_summary",
	],
	"monthly": [
		"velara.tasks.generate_monthly_statistics",
		"velara.tasks.update_dynamic_pricing_rules",
		"velara.tasks.archive_old_folios",
	],
}

# Fixtures
# ------------------
fixtures = [
	{"dt": "Custom Field", "filters": [["module", "in", [
		"Velara", "Velara Setup", "Velara Rooms",
		"Velara Reservations", "Velara Front Desk"]]]},
	{"dt": "Property Setter", "filters": [["module", "in", ["Velara", "Velara Setup"]]]},
	{"dt": "Role", "filters": [["name", "like", "Velara%"]]},
	{"dt": "Number Card", "filters": [["module", "in", ["Velara", "Velara Front Desk",
		"Velara Rooms", "Velara Reservations"]]]},
	{"dt": "Dashboard Chart", "filters": [["module", "in", ["Velara", "Velara Reports"]]]},
	{"dt": "Report", "filters": [["module", "in", ["Velara", "Velara Reports"]]]},
	{"dt": "Workflow State", "filters": [["name", "in", [
		"Draft", "Confirmed", "Guaranteed", "Tentative",
		"Checked In", "Checked Out", "Cancelled", "No Show",
		"Pending", "Assigned", "In Progress", "Inspecting", "Clean", "Dirty",
		"Out of Order", "Out of Service",
		"Open", "Resolved", "Closed",
		"Active", "Expired", "Suspended",
		"Posted", "Settled", "Void",
		"Approved", "Rejected", "On Hold",
		"Completed", "Partially Paid", "Paid"]]]},
	{"dt": "Page", "filters": [["module", "in", ["Velara", "Velara Front Desk"]]]},
	{"dt": "Workflow Action Master", "filters": [["name", "in", [
		"Confirm", "Guarantee", "Check In", "Check Out", "Cancel",
		"Mark No Show", "Assign", "Start Cleaning", "Complete Cleaning",
		"Inspect", "Pass Inspection", "Fail Inspection",
		"Post Charge", "Settle Folio", "Void Charge",
		"Approve", "Reject", "Resolve", "Close", "Reopen",
		"Submit", "Hold", "Resume", "Expire"]]]},
	{"dt": "Workflow", "filters": [["name", "like", "VL%"]]},
	{"dt": "Workspace", "filters": [["module", "like", "Velara%"]]},
	{"dt": "Desktop Icon", "filters": [["app", "=", "velara"]]},
]

# Jinja
# ------------------
jinja = {
	"methods": "velara.utils.jinja_methods",
}

# Override DocType Dashboards
# ------------------
override_doctype_dashboards = {
	"Customer": "velara.overrides.customer_dashboard.get_dashboard_data",
}

# Global Search
# ------------------
global_search_doctypes = {
	"Default": [
		{"doctype": "VL Guest", "index": 1},
		{"doctype": "VL Reservation", "index": 2},
		{"doctype": "VL Room", "index": 3},
		{"doctype": "VL Folio", "index": 4},
		{"doctype": "VL Check In", "index": 5},
		{"doctype": "VL Service Request", "index": 6},
		{"doctype": "VL Event Booking", "index": 7},
		{"doctype": "VL HK Task", "index": 8},
		{"doctype": "VL Maintenance Request", "index": 9},
		{"doctype": "VL Group Booking", "index": 10},
	]
}

export_python_type_annotations = True

default_log_clearing_doctypes = {
	"VL Room Status Log": 30,
}

# ============================================================
# CAPS Integration — Capability-Based Access Control
# ============================================================
caps_capabilities = [
	# Module Access
	{"name": "VL_access_front_desk", "category": "Module", "description": "Access Front Desk module"},
	{"name": "VL_access_reservations", "category": "Module", "description": "Access Reservations module"},
	{"name": "VL_access_rooms", "category": "Module", "description": "Access Rooms module"},
	{"name": "VL_access_housekeeping", "category": "Module", "description": "Access Housekeeping module"},
	{"name": "VL_access_fnb", "category": "Module", "description": "Access Food & Beverage module"},
	{"name": "VL_access_revenue", "category": "Module", "description": "Access Revenue Management module"},
	{"name": "VL_access_guest_services", "category": "Module", "description": "Access Guest Services module"},
	{"name": "VL_access_events", "category": "Module", "description": "Access Events & Banquets module"},
	{"name": "VL_access_maintenance", "category": "Module", "description": "Access Maintenance module"},
	{"name": "VL_access_loyalty", "category": "Module", "description": "Access Loyalty & CRM module"},
	{"name": "VL_access_night_audit", "category": "Module", "description": "Access Night Audit module"},
	{"name": "VL_access_spa", "category": "Module", "description": "Access Spa & Wellness module"},
	{"name": "VL_access_reports", "category": "Module", "description": "Access Reports & Analytics module"},
	{"name": "VL_access_settings", "category": "Module", "description": "Access VELARA Settings"},
	{"name": "VL_access_dashboard", "category": "Module", "description": "Access VELARA Dashboard"},
	# Actions — Front Desk
	{"name": "VL_check_in_guest", "category": "Action", "description": "Perform guest check-in"},
	{"name": "VL_check_out_guest", "category": "Action", "description": "Perform guest check-out"},
	{"name": "VL_assign_room", "category": "Action", "description": "Assign room to reservation"},
	{"name": "VL_change_room", "category": "Action", "description": "Change guest room"},
	{"name": "VL_post_charge", "category": "Action", "description": "Post charge to guest folio"},
	{"name": "VL_settle_folio", "category": "Action", "description": "Settle and close guest folio"},
	{"name": "VL_void_charge", "category": "Action", "description": "Void a posted charge"},
	{"name": "VL_issue_key_card", "category": "Action", "description": "Issue/reissue key cards"},
	# Actions — Reservations
	{"name": "VL_create_reservation", "category": "Action", "description": "Create new reservations"},
	{"name": "VL_modify_reservation", "category": "Action", "description": "Modify existing reservations"},
	{"name": "VL_cancel_reservation", "category": "Action", "description": "Cancel reservations"},
	{"name": "VL_confirm_reservation", "category": "Action", "description": "Confirm tentative reservations"},
	{"name": "VL_create_group_booking", "category": "Action", "description": "Create group bookings"},
	# Actions — Housekeeping
	{"name": "VL_assign_hk_task", "category": "Action", "description": "Assign housekeeping tasks"},
	{"name": "VL_complete_hk_task", "category": "Action", "description": "Mark cleaning complete"},
	{"name": "VL_inspect_room", "category": "Action", "description": "Perform room inspection"},
	{"name": "VL_override_room_status", "category": "Action", "description": "Override room status"},
	# Actions — Revenue
	{"name": "VL_override_rate", "category": "Action", "description": "Override standard room rates"},
	{"name": "VL_apply_discount", "category": "Action", "description": "Apply discounts to reservations"},
	{"name": "VL_manage_rate_plans", "category": "Action", "description": "Create/edit rate plans"},
	{"name": "VL_manage_channels", "category": "Action", "description": "Configure channel manager"},
	# Actions — Guest Services
	{"name": "VL_create_service_request", "category": "Action", "description": "Create service requests"},
	{"name": "VL_resolve_service_request", "category": "Action", "description": "Resolve service requests"},
	{"name": "VL_approve_complimentary", "category": "Action", "description": "Approve complimentary services"},
	# Actions — Events
	{"name": "VL_create_event_booking", "category": "Action", "description": "Create event bookings"},
	{"name": "VL_approve_event_booking", "category": "Action", "description": "Approve event bookings"},
	# Actions — Night Audit
	{"name": "VL_run_night_audit", "category": "Action", "description": "Execute night audit process"},
	{"name": "VL_close_business_day", "category": "Action", "description": "Close business day"},
	# Actions — Maintenance
	{"name": "VL_create_maintenance_req", "category": "Action", "description": "Create maintenance requests"},
	{"name": "VL_resolve_maintenance", "category": "Action", "description": "Resolve maintenance requests"},
	# Actions — Loyalty
	{"name": "VL_enroll_loyalty", "category": "Action", "description": "Enroll guests in loyalty program"},
	{"name": "VL_redeem_points", "category": "Action", "description": "Redeem loyalty points"},
	# Actions — Spa
	{"name": "VL_create_spa_booking", "category": "Action", "description": "Create spa bookings"},
	# Field-Level
	{"name": "VL_view_revenue_data", "category": "Field", "description": "View revenue/financial data"},
	{"name": "VL_view_cost_data", "category": "Field", "description": "View cost and expense data"},
	{"name": "VL_view_guest_payment_info", "category": "Field", "description": "View guest payment details"},
	{"name": "VL_view_occupancy_forecast", "category": "Field", "description": "View occupancy forecast"},
	{"name": "VL_view_rate_plans", "category": "Field", "description": "View rate plan configurations"},
	{"name": "VL_view_staff_tips", "category": "Field", "description": "View staff tips data"},
	# Reports
	{"name": "VL_export_reports", "category": "Report", "description": "Export reports to PDF/Excel"},
	{"name": "VL_view_revenue_reports", "category": "Report", "description": "View revenue reports"},
	{"name": "VL_view_occupancy_reports", "category": "Report", "description": "View occupancy reports"},
	{"name": "VL_view_guest_reports", "category": "Report", "description": "View guest analytics"},
	{"name": "VL_view_housekeeping_reports", "category": "Report", "description": "View HK reports"},
	{"name": "VL_view_financial_reports", "category": "Report", "description": "View financial reports"},
]

caps_field_maps = [
	{"capability": "VL_view_revenue_data", "doctype": "VL Folio", "field": "total_amount", "behavior": "hide"},
	{"capability": "VL_view_revenue_data", "doctype": "VL Folio", "field": "balance", "behavior": "hide"},
	{"capability": "VL_view_revenue_data", "doctype": "VL Night Audit", "field": "total_revenue", "behavior": "hide"},
	{"capability": "VL_view_cost_data", "doctype": "VL Rate Plan", "field": "cost_per_night", "behavior": "hide"},
	{"capability": "VL_view_cost_data", "doctype": "VL Event Booking", "field": "total_cost", "behavior": "hide"},
	{"capability": "VL_view_guest_payment_info", "doctype": "VL Guest", "field": "card_number", "behavior": "mask"},
	{"capability": "VL_view_rate_plans", "doctype": "VL Rate Plan", "field": "base_rate", "behavior": "hide"},
	{"capability": "VL_view_staff_tips", "doctype": "VL Folio Charge", "field": "tip_amount", "behavior": "hide"},
	{"capability": "VL_view_occupancy_forecast", "doctype": "VL Night Audit", "field": "forecast_occupancy", "behavior": "hide"},
]

# Website Route Rules
# --------------------------------------------------------
website_route_rules = [
    {"from_route": "/velara-about", "to_route": "velara_about"},
    {"from_route": "/velara-onboarding", "to_route": "velara_onboarding"},
    {"from_route": "/عن-velara", "to_route": "velara_about"},
    {"from_route": "/velara/<path:app_path>", "to_route": "velara/<app_path>"},
]
