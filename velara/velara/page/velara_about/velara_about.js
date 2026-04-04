// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT

frappe.pages["velara-about"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("About Velara"),
        single_column: true,
    });

    page.main.addClass("velara-about-page");
    const $container = $('<div class="fv-about-container"></div>').appendTo(page.main);

    // Use frappe.visual.generator for premium rendering
    const renderWithGenerator = async () => {
        try {
            await frappe.visual.generator.aboutPage(
                $container[0],
                "velara",
                {
                    color: "#8B5CF6",
                    mainDoctype: "VL Reservation",
                    features: [
        {
                "icon": "door-enter",
                "title": "Front Desk",
                "description": "Check-in/out, room assignment, guest profiles, and live room rack."
        },
        {
                "icon": "bed",
                "title": "Room Management",
                "description": "Room types, inventory, housekeeping status, and maintenance tracking."
        },
        {
                "icon": "calendar-event",
                "title": "Reservations",
                "description": "Direct and OTA bookings, availability calendar, and rate management."
        },
        {
                "icon": "broom",
                "title": "Housekeeping",
                "description": "Room cleaning schedules, assignments, inspections, and status tracking."
        },
        {
                "icon": "tools-kitchen-2",
                "title": "Food & Beverage",
                "description": "Restaurant, room service, minibar, and banquet management."
        },
        {
                "icon": "spa",
                "title": "Spa & Wellness",
                "description": "Treatment bookings, therapist scheduling, and package management."
        },
        {
                "icon": "calendar-stats",
                "title": "Events",
                "description": "Conference rooms, event bookings, setup requirements, and billing."
        },
        {
                "icon": "report-money",
                "title": "Revenue & Night Audit",
                "description": "Rate plans, revenue tracking, night audit, and financial reports."
        }
],
                    roles: [
        {
                "name": "VL Front Desk",
                "icon": "door-enter",
                "description": "Check-in/out, guest management, and room assignment."
        },
        {
                "name": "VL Housekeeper",
                "icon": "broom",
                "description": "Room cleaning, inspection, and supply tracking."
        },
        {
                "name": "VL F&B Manager",
                "icon": "tools-kitchen-2",
                "description": "Restaurant, room service, and banquet operations."
        },
        {
                "name": "VL Revenue Manager",
                "icon": "report-money",
                "description": "Rate management, night audit, and financial reporting."
        }
],
                    ctas: [
                        { label: __("Start Onboarding"), route: "velara-onboarding", primary: true },
                        { label: __("Open Settings"), route: "app/vl-settings" },
                    ],
                }
            );
        } catch(e) {
            console.warn("Generator failed, using fallback:", e);
            renderFallback($container);
        }
    };

    const renderFallback = ($el) => {
        $el.html(`
            <div style="text-align:center;padding:60px 20px">
                <h1 style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#333);-webkit-background-clip:text;-webkit-text-fill-color:transparent">${__("Velara")}</h1>
                <p style="font-size:1.15rem;color:var(--text-muted);max-width:600px;margin:16px auto">${__("Check-in/out, room assignment, guest profiles, and live room rack.")}</p>
                <div style="margin-top:24px">
                    <a href="/app/velara-onboarding" class="btn btn-primary btn-lg">${__("Start Onboarding")}</a>
                </div>
            </div>
        `);
    };

    if (frappe.visual && frappe.visual.generator) {
        renderWithGenerator();
    } else {
        frappe.require("frappe_visual.bundle.js", () => {
            if (frappe.visual && frappe.visual.generator) {
                renderWithGenerator();
            } else {
                renderFallback($container);
            }
        });
    }
};
