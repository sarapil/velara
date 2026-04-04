// Copyright (c) 2024, Arkan Lab — https://arkan.it.com
// License: MIT
// frappe_visual Integration for Velara

(function() {
    "use strict";

    // App branding registration
    const APP_CONFIG = {
        name: "velara",
        title: __("Velara"),
        color: "#8B5CF6",
        module: "Velara Front Desk",
    };

    // Initialize visual enhancements when ready
    $(document).on("app_ready", function() {
        // Register app color with visual theme system
        if (frappe.visual && frappe.visual.ThemeManager) {
            try {
                document.documentElement.style.setProperty(
                    "--velara-primary",
                    APP_CONFIG.color
                );
            } catch(e) {}
        }

        // Initialize bilingual tooltips for Arabic support
        if (frappe.visual && frappe.visual.bilingualTooltip) {
            // bilingualTooltip auto-initializes — just ensure it's active
        }
    });

    // Route-based visual page rendering
    $(document).on("page-change", function() {
        if (!frappe.visual || !frappe.visual.generator) return;

    // Visual Settings Page
    if (frappe.get_route_str() === 'velara-settings') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.settingsPage(
                page.main[0] || page.main,
                "VL Settings"
            );
        }
    }

    // Visual Reports Hub
    if (frappe.get_route_str() === 'velara-reports') {
        const page = frappe.container.page;
        if (page && page.main && frappe.visual.generator) {
            frappe.visual.generator.reportsHub(
                page.main[0] || page.main,
                "Velara Front Desk"
            );
        }
    }
    });
})();
