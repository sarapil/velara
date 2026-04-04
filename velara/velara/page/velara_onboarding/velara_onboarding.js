// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT

frappe.pages["velara-onboarding"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Velara Onboarding"),
        single_column: true,
    });

    page.main.addClass("velara-onboarding-page");
    const $container = $('<div class="fv-onboarding-container"></div>').appendTo(page.main);

    const steps = [
        {
                "title": "Hotel Setup",
                "description": "Configure your property details, room types, and rate plans.",
                "icon": "building"
        },
        {
                "title": "App Structure",
                "description": "Explore all Velara modules.",
                "icon": "sitemap",
                "component": "app-map"
        },
        {
                "title": "Room Configuration",
                "description": "Set up rooms, floors, and housekeeping schedules.",
                "icon": "bed"
        },
        {
                "title": "Data Model",
                "description": "See how reservations, rooms, guests, and billing connect.",
                "icon": "hierarchy-2",
                "component": "erd",
                "doctype": "VL Reservation"
        },
        {
                "title": "Rate Plans",
                "description": "Create rate plans, seasons, and pricing rules.",
                "icon": "report-money"
        },
        {
                "title": "Staff Setup",
                "description": "Define roles for front desk, housekeeping, F&B, and management.",
                "icon": "users"
        },
        {
                "title": "Go Live",
                "description": "Start accepting reservations and managing your hotel.",
                "icon": "rocket"
        }
];

    // Use frappe.visual.generator for premium wizard rendering
    const renderWithGenerator = () => {
        try {
            frappe.visual.generator.onboardingWizard(
                $container[0],
                "Velara",
                steps.map(s => ({
                    ...s,
                    onComplete: s.title.includes("rocket") || s.title.includes("Ready") || s.title.includes("Go Live") || s.title.includes("Start")
                        ? () => frappe.set_route("app")
                        : undefined,
                }))
            );
        } catch(e) {
            console.warn("Generator failed, using fallback:", e);
            renderFallback($container, steps);
        }
    };

    const renderFallback = ($el, steps) => {
        const stepsHtml = steps.map((s, i) => `
            <div style="display:flex;gap:16px;padding:20px 0;border-bottom:1px solid var(--border-color)">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(99,102,241,0.1);color:#8B5CF6;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">${i+1}</div>
                <div><h3 style="font-size:1rem;font-weight:600;margin-bottom:4px">${__(s.title)}</h3><p style="font-size:0.9rem;color:var(--text-muted)">${__(s.description)}</p></div>
            </div>
        `).join('');
        $el.html(`
            <div style="text-align:center;padding:60px 20px">
                <h1>🚀 ${__("Get Started with Velara")}</h1>
                <p style="color:var(--text-muted)">${__("Follow these steps to set up and master Velara.")}</p>
            </div>
            <div style="max-width:700px;margin:0 auto;padding:0 20px">${stepsHtml}</div>
        `);
    };

    if (frappe.visual && frappe.visual.generator) {
        renderWithGenerator();
    } else {
        frappe.require("frappe_visual.bundle.js", () => {
            if (frappe.visual && frappe.visual.generator) {
                renderWithGenerator();
            } else {
                renderFallback($container, steps);
            }
        });
    }
};
