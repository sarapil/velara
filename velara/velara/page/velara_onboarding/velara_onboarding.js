// Copyright (c) 2026, Arkan Lab — https://arkan.it.com
// License: MIT

frappe.pages["velara-onboarding"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Velara Onboarding — إعداد فيلارا"),
        single_column: true,
    });

    page.main.addClass("velara-onboarding-page");
    new VelaraOnboarding(page);
};

class VelaraOnboarding {
    constructor(page) {
        this.page = page;
        this.current_step = 0;
        this.completed_steps = new Set();
        this.steps = this.get_steps();
        this.init();
    }

    async init() {
        try {
            await frappe.require("frappe_visual.bundle.js");
        } catch (e) {
            console.warn("frappe_visual not available, using fallback");
        }
        this.render();
    }

    get_steps() {
        return [
            {
                key: "welcome",
                title: __("Welcome to Velara"),
                title_ar: "مرحباً بك في فيلارا",
                icon: "building",
                description: __("Complete hotel property management: reservations, front desk, housekeeping, billing, and guest relations."),
            },
            {
                key: "property_setup",
                title: __("Property Setup"),
                title_ar: "إعداد الفندق",
                icon: "building-community",
                description: __("Configure your hotel property details, stars, amenities, and operational settings."),
            },
            {
                key: "room_config",
                title: __("Room Configuration"),
                title_ar: "إعداد الغرف",
                icon: "bed",
                description: __("Define room types, floors, rooms, amenities, and housekeeping schedules."),
            },
            {
                key: "rate_plans",
                title: __("Rate Plans & Pricing"),
                title_ar: "خطط الأسعار",
                icon: "report-money",
                description: __("Create rate plans, seasonal pricing, packages, and revenue rules."),
            },
            {
                key: "roles_team",
                title: __("Roles & Team"),
                title_ar: "الأدوار والفريق",
                icon: "users",
                description: __("Assign roles: Front Desk Agent, Housekeeping, Revenue Manager, General Manager."),
            },
            {
                key: "reservation_workflow",
                title: __("Reservation Workflow"),
                title_ar: "سير عمل الحجوزات",
                icon: "arrows-sort",
                description: __("Understand the guest lifecycle: Inquiry → Reservation → Check-In → Stay → Check-Out."),
            },
            {
                key: "front_desk",
                title: __("Front Desk Operations"),
                title_ar: "عمليات الاستقبال",
                icon: "layout-dashboard",
                description: __("Check-in, check-out, room assignments, guest folios, and walk-in management."),
            },
            {
                key: "housekeeping",
                title: __("Housekeeping"),
                title_ar: "التدبير المنزلي",
                icon: "wand",
                description: __("Room status tracking, task assignment, inspection checklists, and maintenance requests."),
            },
            {
                key: "advanced",
                title: __("Advanced Features"),
                title_ar: "الميزات المتقدمة",
                icon: "sparkles",
                description: __("Revenue management, channel integration, guest loyalty, and analytics."),
            },
            {
                key: "go_live",
                title: __("Go Live!"),
                title_ar: "!ابدأ العمل",
                icon: "rocket",
                description: __("Final checks and start accepting reservations."),
            },
        ];
    }

    render() {
        const $main = $(this.page.main);
        $main.empty();

        $main.html(`
            <div class="fv-onboarding-wrapper" style="max-width:1100px;margin:0 auto;padding:24px">
                <div class="fv-fx-page-enter" id="onboarding-header"></div>
                <div class="fv-fx-page-enter" id="onboarding-progress" style="margin:24px 0"></div>
                <div class="fv-fx-page-enter" id="onboarding-content" style="margin-top:20px"></div>
                <div id="onboarding-nav" style="margin-top:24px"></div>
            </div>
        `);

        this.render_header();
        this.render_progress();
        this.render_step_content();
        this.render_navigation();
    }

    render_header() {
        const stats_html = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:16px;margin-top:20px">
                ${this.stat_card("🛏️", __("Total Rooms"), "VL Room")}
                ${this.stat_card("📋", __("Reservations"), "VL Reservation")}
                ${this.stat_card("👤", __("Guests"), "VL Guest")}
                ${this.stat_card("🧹", __("Housekeeping Tasks"), "VL Housekeeping Task")}
            </div>
        `;

        $("#onboarding-header").html(`
            <div class="fv-fx-glass" style="padding:32px;border-radius:16px;text-align:center">
                <div style="font-size:3rem;margin-bottom:8px">🏨</div>
                <h1 style="font-size:1.8rem;font-weight:700;margin:0">
                    ${__("Velara Hotel Property Management")}
                </h1>
                <p style="color:var(--text-muted);font-size:1.05rem;margin:8px 0 0">
                    ${__("نظام إدارة الفنادق الشامل — Complete Hospitality Operations")}
                </p>
                ${stats_html}
            </div>
        `);

        this.load_stat_counts();
    }

    stat_card(emoji, label, doctype) {
        return `
            <div class="fv-fx-hover-lift" style="background:var(--card-bg);border-radius:12px;padding:16px;text-align:center;border:1px solid var(--border-color)">
                <div style="font-size:1.5rem">${emoji}</div>
                <div id="stat-${doctype.replace(/\s/g, '-')}" style="font-size:1.4rem;font-weight:700;color:var(--text-color)">—</div>
                <div style="font-size:0.8rem;color:var(--text-muted)">${label}</div>
            </div>
        `;
    }

    load_stat_counts() {
        const doctypes = ["VL Room", "VL Reservation", "VL Guest", "VL Housekeeping Task"];
        doctypes.forEach((dt) => {
            frappe.xcall("frappe.client.get_count", { doctype: dt }).then((count) => {
                $(`#stat-${dt.replace(/\s/g, '-')}`).text(count || 0);
            }).catch(() => {
                $(`#stat-${dt.replace(/\s/g, '-')}`).text("—");
            });
        });
    }

    render_progress() {
        const total = this.steps.length;
        const pct = Math.round(((this.completed_steps.size) / total) * 100);

        const dots = this.steps.map((s, i) => {
            const is_done = this.completed_steps.has(i);
            const is_active = i === this.current_step;
            const bg = is_done ? "#C9A84C" : is_active ? "#A88832" : "var(--border-color)";
            const scale = is_active ? "transform:scale(1.3)" : "";
            return `<div style="width:${is_active ? 14 : 10}px;height:${is_active ? 14 : 10}px;border-radius:50%;background:${bg};transition:all .3s;${scale};cursor:pointer" data-step="${i}" class="progress-dot"></div>`;
        }).join("");

        $("#onboarding-progress").html(`
            <div style="display:flex;align-items:center;gap:12px">
                <div style="flex:1;height:6px;border-radius:3px;background:var(--border-color);overflow:hidden">
                    <div style="width:${pct}%;height:100%;background:linear-gradient(90deg,#C9A84C,#A88832);border-radius:3px;transition:width .5s"></div>
                </div>
                <span style="font-size:0.85rem;font-weight:600;color:#C9A84C">${pct}%</span>
            </div>
            <div style="display:flex;justify-content:center;gap:8px;margin-top:12px">${dots}</div>
        `);

        $("#onboarding-progress").find(".progress-dot").on("click", (e) => {
            this.current_step = parseInt($(e.target).data("step"));
            this.render_progress();
            this.render_step_content();
            this.render_navigation();
        });
    }

    render_step_content() {
        const step = this.steps[this.current_step];
        const content_fn = this[`render_${step.key}`];
        const $el = $("#onboarding-content");

        $el.html(`
            <div class="fv-fx-glass" style="padding:32px;border-radius:16px">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
                    <div style="width:48px;height:48px;border-radius:12px;background:rgba(201,168,76,0.15);color:#C9A84C;display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:700">
                        ${this.current_step + 1}
                    </div>
                    <div>
                        <h2 style="font-size:1.3rem;font-weight:700;margin:0">${step.title}</h2>
                        <p style="font-size:0.85rem;color:var(--text-muted);margin:0">${step.title_ar}</p>
                    </div>
                </div>
                <p style="color:var(--text-muted);font-size:1rem;margin-bottom:20px">${step.description}</p>
                <div id="step-body"></div>
            </div>
        `);

        if (content_fn) {
            content_fn.call(this, $("#step-body"));
        }
    }

    render_welcome($el) {
        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px">
                ${this.feature_card("📋", __("Reservations"), __("Online & walk-in bookings, calendar view, availability management"))}
                ${this.feature_card("🛎️", __("Front Desk"), __("Check-in, check-out, room assignment, guest folios"))}
                ${this.feature_card("🛏️", __("Room Management"), __("Room types, floors, status tracking, maintenance"))}
                ${this.feature_card("🧹", __("Housekeeping"), __("Task scheduling, inspections, staff assignment, status board"))}
                ${this.feature_card("💰", __("Billing & Folio"), __("Guest charges, payments, invoicing, split billing"))}
                ${this.feature_card("👤", __("Guest Relations"), __("Guest profiles, preferences, loyalty, history"))}
                ${this.feature_card("📊", __("Revenue Management"), __("Rates, occupancy analytics, RevPAR, forecasting"))}
                ${this.feature_card("🔗", __("Channel Manager"), __("OTA integration, rate parity, inventory sync"))}
            </div>
        `);
    }

    render_property_setup($el) {
        const actions = [
            { label: __("Hotel Settings"), route: "vl-hotel-settings", icon: "⚙️" },
            { label: __("Add Property"), route: "vl-property/new", icon: "🏨" },
            { label: __("Room Types"), route: "vl-room-type", icon: "🏷️" },
            { label: __("Amenities"), route: "vl-amenity", icon: "🛁" },
        ];

        $el.html(`
            <div style="margin-bottom:20px">
                <h4 style="font-weight:600">${__("Quick Setup Actions — إجراءات الإعداد السريع")}</h4>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px">
                    ${actions.map(a => `
                        <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:16px;cursor:pointer;text-align:center"
                             onclick="frappe.set_route('${a.route}')">
                            <div style="font-size:2rem;margin-bottom:8px">${a.icon}</div>
                            <div style="font-size:0.9rem;font-weight:600">${a.label}</div>
                        </div>
                    `).join("")}
                </div>
            </div>
            <div class="fv-fx-glass" style="padding:20px;border-radius:12px;background:rgba(201,168,76,0.05)">
                <h4 style="font-weight:600">${__("Setup Checklist — قائمة الإعداد")}</h4>
                ${this.checklist_item(__("Hotel name, address & contact configured"))}
                ${this.checklist_item(__("At least one property created"))}
                ${this.checklist_item(__("Room types defined (Standard, Deluxe, Suite, etc.)"))}
                ${this.checklist_item(__("Amenities list populated"))}
                ${this.checklist_item(__("Tax and service charge configured"))}
            </div>
        `);
    }

    render_room_config($el) {
        const actions = [
            { label: __("Add Floor"), route: "vl-floor/new", icon: "🏢" },
            { label: __("Add Room"), route: "vl-room/new", icon: "🚪" },
            { label: __("Room Types"), route: "vl-room-type", icon: "🏷️" },
            { label: __("Housekeeping Schedule"), route: "vl-housekeeping-schedule", icon: "📅" },
        ];

        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px">
                ${actions.map(a => `
                    <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:16px;cursor:pointer;text-align:center"
                         onclick="frappe.set_route('${a.route}')">
                        <div style="font-size:2rem;margin-bottom:8px">${a.icon}</div>
                        <div style="font-size:0.9rem;font-weight:600">${a.label}</div>
                    </div>
                `).join("")}
            </div>
            <div style="background:var(--card-bg);border-radius:12px;padding:20px;border:1px solid var(--border-color)">
                <h4 style="font-weight:600">${__("Room Hierarchy — هيكل الغرف")}</h4>
                <div style="font-family:monospace;font-size:0.85rem;line-height:2;color:var(--text-muted)">
                    🏨 ${__("Property")} (${__("e.g. Velara Downtown, Velara Beach")})<br>
                    &nbsp;&nbsp;└── 🏢 ${__("Floor")} (${__("floor number, wing, section")})<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 🚪 ${__("Room")} (${__("number, type, status, max occupancy")})<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 🛁 ${__("Amenities")} (${__("WiFi, minibar, safe, TV, AC")})<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 🧹 ${__("Housekeeping Status")} (${__("Clean, Dirty, Inspected, OOO")})
                </div>
            </div>
        `);
    }

    render_rate_plans($el) {
        const actions = [
            { label: __("Add Rate Plan"), route: "vl-rate-plan/new", icon: "💲" },
            { label: __("Season Pricing"), route: "vl-season", icon: "🌞" },
            { label: __("Packages"), route: "vl-package", icon: "📦" },
        ];

        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px">
                ${actions.map(a => `
                    <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:16px;cursor:pointer;text-align:center"
                         onclick="frappe.set_route('${a.route}')">
                        <div style="font-size:2rem;margin-bottom:8px">${a.icon}</div>
                        <div style="font-size:0.9rem;font-weight:600">${a.label}</div>
                    </div>
                `).join("")}
            </div>
            <div class="fv-fx-glass" style="padding:20px;border-radius:12px">
                <h4 style="font-weight:600">${__("Pricing Strategy — استراتيجية التسعير")}</h4>
                <div style="font-size:0.9rem;line-height:2;color:var(--text-muted)">
                    1️⃣ ${__("Define base rates per room type (BAR — Best Available Rate)")}<br>
                    2️⃣ ${__("Create seasons (Peak, Shoulder, Low) with multipliers")}<br>
                    3️⃣ ${__("Set weekend/weekday rate differences")}<br>
                    4️⃣ ${__("Build packages (B&B, Half Board, All Inclusive)")}<br>
                    5️⃣ ${__("Configure promotional & corporate rates")}
                </div>
            </div>
        `);
    }

    render_roles_team($el) {
        const roles = [
            { role: __("VL General Manager"), desc: __("Full access: all operations, reports, revenue, staff"), color: "#C9A84C", icon: "👔" },
            { role: __("VL Front Desk Agent"), desc: __("Reservations, check-in/out, guest folios, room assignments"), color: "#3B82F6", icon: "🛎️" },
            { role: __("VL Housekeeping Manager"), desc: __("Task assignment, inspections, room status, maintenance"), color: "#10B981", icon: "🧹" },
            { role: __("VL Revenue Manager"), desc: __("Rate plans, pricing, channel management, analytics"), color: "#8B5CF6", icon: "📊" },
            { role: __("VL Concierge"), desc: __("Guest services, requests, transportation, local info"), color: "#F59E0B", icon: "🎩" },
            { role: __("VL F&B Manager"), desc: __("Room service, restaurant, minibar, meal plans"), color: "#EF4444", icon: "🍽️" },
        ];

        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px">
                ${roles.map(r => `
                    <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:18px;border-inline-start:4px solid ${r.color}">
                        <div style="font-size:1.6rem;margin-bottom:6px">${r.icon}</div>
                        <div style="font-weight:700;font-size:0.95rem;color:${r.color}">${r.role}</div>
                        <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px">${r.desc}</div>
                    </div>
                `).join("")}
            </div>
        `);
    }

    render_reservation_workflow($el) {
        const states = [
            { label: __("Inquiry"), icon: "📞", color: "#64748B", desc: __("Guest inquires about availability") },
            { label: __("Reserved"), icon: "📋", color: "#3B82F6", desc: __("Reservation confirmed, deposit taken") },
            { label: __("Check-In"), icon: "🛎️", color: "#C9A84C", desc: __("Guest arrives, ID verified, key issued") },
            { label: __("In-House"), icon: "🏨", color: "#10B981", desc: __("Guest staying, charges accumulate") },
            { label: __("Check-Out"), icon: "🚪", color: "#8B5CF6", desc: __("Folio settled, feedback collected") },
            { label: __("Post-Stay"), icon: "⭐", color: "#F59E0B", desc: __("Review, loyalty points, follow-up") },
        ];

        $el.html(`
            <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:center">
                ${states.map((s, i) => `
                    <div style="display:flex;align-items:center;gap:8px">
                        <div class="fv-fx-hover-lift" style="background:${s.color}15;border:2px solid ${s.color};border-radius:12px;padding:14px 18px;text-align:center;min-width:120px">
                            <div style="font-size:1.5rem">${s.icon}</div>
                            <div style="font-size:0.85rem;font-weight:700;color:${s.color};margin-top:4px">${s.label}</div>
                            <div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px">${s.desc}</div>
                        </div>
                        ${i < states.length - 1 ? '<div style="font-size:1.2rem;color:var(--text-muted)">→</div>' : ''}
                    </div>
                `).join("")}
            </div>
        `);
    }

    render_front_desk($el) {
        const actions = [
            { label: __("New Reservation"), route: "vl-reservation/new", icon: "📋" },
            { label: __("Today's Arrivals"), route: "vl-reservation?check_in=Today&status=Confirmed", icon: "🛬" },
            { label: __("Today's Departures"), route: "vl-reservation?check_out=Today&status=Checked In", icon: "🛫" },
            { label: __("Room Status Board"), route: "vl-room?view=Report", icon: "🗺️" },
        ];

        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px">
                ${actions.map(a => `
                    <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:16px;cursor:pointer;text-align:center"
                         onclick="frappe.set_route('${a.route}')">
                        <div style="font-size:2rem;margin-bottom:8px">${a.icon}</div>
                        <div style="font-size:0.9rem;font-weight:600">${a.label}</div>
                    </div>
                `).join("")}
            </div>
            <div class="fv-fx-glass" style="padding:20px;border-radius:12px">
                <h4 style="font-weight:600">${__("Daily Front Desk Routine — الروتين اليومي للاستقبال")}</h4>
                <div style="font-size:0.9rem;line-height:2;color:var(--text-muted)">
                    ☀️ ${__("Morning: Review arrivals, check room readiness, prepare keys")}<br>
                    🛎️ ${__("Check-In: Verify ID, assign room, collect deposit, issue key card")}<br>
                    📝 ${__("During Stay: Handle requests, post charges to folio, coordinate housekeeping")}<br>
                    🚪 ${__("Check-Out: Review folio, process payment, collect key, request feedback")}<br>
                    🌙 ${__("Night Audit: Close day, reconcile revenues, generate reports")}
                </div>
            </div>
        `);
    }

    render_housekeeping($el) {
        const actions = [
            { label: __("Task Board"), route: "vl-housekeeping-task?status=Open", icon: "📋" },
            { label: __("Room Status"), route: "vl-room?view=Report", icon: "🧹" },
            { label: __("Maintenance"), route: "vl-maintenance-request", icon: "🔧" },
        ];

        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px">
                ${actions.map(a => `
                    <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:16px;cursor:pointer;text-align:center"
                         onclick="frappe.set_route('${a.route}')">
                        <div style="font-size:2rem;margin-bottom:8px">${a.icon}</div>
                        <div style="font-size:0.9rem;font-weight:600">${a.label}</div>
                    </div>
                `).join("")}
            </div>
            <div style="background:var(--card-bg);border-radius:12px;padding:20px;border:1px solid var(--border-color)">
                <h4 style="font-weight:600">${__("Room Status Cycle — دورة حالة الغرف")}</h4>
                <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px">
                    ${[
                        "🔴 " + __("Dirty"),
                        "🟡 " + __("Cleaning"),
                        "🟢 " + __("Clean"),
                        "✅ " + __("Inspected"),
                        "🏨 " + __("Occupied"),
                        "🔧 " + __("Maintenance"),
                        "🚫 " + __("Out of Order"),
                        "📋 " + __("Available"),
                    ].map(s =>
                        `<span style="background:var(--bg-color);border:1px solid var(--border-color);border-radius:20px;padding:6px 14px;font-size:0.8rem">${s}</span>`
                    ).join("")}
                </div>
            </div>
        `);
    }

    render_advanced($el) {
        const features = [
            { title: __("Revenue Management"), desc: __("Dynamic pricing, RevPAR optimization, demand forecasting"), icon: "📈" },
            { title: __("Channel Manager"), desc: __("Sync rates & inventory with Booking.com, Expedia, Airbnb"), icon: "🔗" },
            { title: __("Guest Loyalty"), desc: __("Points program, tier benefits, special amenities"), icon: "⭐" },
            { title: __("Night Audit"), desc: __("Automated day-end closing, revenue reconciliation"), icon: "🌙" },
            { title: __("Guest Communications"), desc: __("Pre-arrival emails, in-stay messaging, post-stay surveys"), icon: "✉️" },
            { title: __("Reports & Analytics"), desc: __("Occupancy, ADR, RevPAR, guest demographics, source analysis"), icon: "📊" },
        ];

        $el.html(`
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px">
                ${features.map(f => `
                    <div class="fv-fx-hover-lift fv-fx-glass" style="padding:18px;border-radius:12px">
                        <div style="font-size:1.6rem;margin-bottom:8px">${f.icon}</div>
                        <div style="font-weight:700;font-size:0.95rem">${f.title}</div>
                        <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px">${f.desc}</div>
                    </div>
                `).join("")}
            </div>
        `);
    }

    render_go_live($el) {
        $el.html(`
            <div style="text-align:center;padding:20px">
                <div style="font-size:4rem;margin-bottom:16px">🎉</div>
                <h3 style="font-weight:700">${__("Your Hotel is Ready!")}</h3>
                <p style="color:var(--text-muted)">${__("فندقك جاهز للعمل! — Review the checklist below and open your doors.")}</p>
            </div>
            <div class="fv-fx-glass" style="padding:24px;border-radius:12px;margin-top:16px">
                <h4 style="font-weight:600">${__("Launch Checklist — قائمة الإطلاق")}</h4>
                ${this.checklist_item(__("Hotel property and settings configured"))}
                ${this.checklist_item(__("All rooms created with types and amenities"))}
                ${this.checklist_item(__("Rate plans and seasonal pricing set"))}
                ${this.checklist_item(__("Roles assigned to all team members"))}
                ${this.checklist_item(__("Housekeeping schedules defined"))}
                ${this.checklist_item(__("Test reservation created and checked in"))}
                ${this.checklist_item(__("Night audit process tested"))}
                ${this.checklist_item(__("Guest registration card printed"))}
            </div>
            <div style="text-align:center;margin-top:24px">
                <button class="btn btn-primary btn-lg" onclick="frappe.set_route('velara-dashboard')" style="background:#C9A84C;border-color:#C9A84C;padding:12px 40px;font-size:1rem;border-radius:12px">
                    ${__("Open Dashboard — فتح لوحة التحكم")} 🚀
                </button>
            </div>
        `);
    }

    feature_card(icon, title, desc) {
        return `
            <div class="fv-fx-hover-lift" style="background:var(--card-bg);border:1px solid var(--border-color);border-radius:12px;padding:18px">
                <div style="font-size:1.6rem;margin-bottom:8px">${icon}</div>
                <div style="font-weight:700;font-size:0.9rem">${title}</div>
                <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px">${desc}</div>
            </div>
        `;
    }

    checklist_item(label) {
        return `
            <div style="display:flex;align-items:center;gap:10px;padding:6px 0">
                <div style="width:20px;height:20px;border-radius:4px;border:2px solid var(--border-color);flex-shrink:0"></div>
                <span style="font-size:0.9rem">${label}</span>
            </div>
        `;
    }

    render_navigation() {
        const $nav = $("#onboarding-nav");
        const is_first = this.current_step === 0;
        const is_last = this.current_step === this.steps.length - 1;

        $nav.html(`
            <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 0;border-top:1px solid var(--border-color)">
                <button class="btn btn-default btn-sm" ${is_first ? 'disabled' : ''} id="btn-prev"
                        style="border-radius:8px;padding:8px 20px">
                    ← ${__("Previous — السابق")}
                </button>
                <span style="font-size:0.85rem;color:var(--text-muted)">
                    ${this.current_step + 1} / ${this.steps.length}
                </span>
                <button class="btn btn-primary btn-sm" id="btn-next"
                        style="border-radius:8px;padding:8px 20px;background:#C9A84C;border-color:#C9A84C">
                    ${is_last ? __("Finish") + " ✓" : __("Next — التالي") + " →"}
                </button>
            </div>
        `);

        $nav.find("#btn-prev").on("click", () => {
            if (this.current_step > 0) {
                this.completed_steps.add(this.current_step);
                this.current_step--;
                this.render_progress();
                this.render_step_content();
                this.render_navigation();
            }
        });

        $nav.find("#btn-next").on("click", () => {
            this.completed_steps.add(this.current_step);
            if (this.current_step < this.steps.length - 1) {
                this.current_step++;
                this.render_progress();
                this.render_step_content();
                this.render_navigation();
            } else {
                frappe.set_route("velara-dashboard");
            }
        });
    }
}
