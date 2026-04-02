"""
Velara Hotel Management — Seed Data
Creates essential reference/lookup data for a fresh Velara installation.

Usage:
    bench --site dev.localhost execute velara.setup.seed.run
"""

import frappe
from frappe import _
from frappe.utils import add_months, getdate, nowdate


def run():
    """Main entry point for seeding Velara reference data."""
    frappe.flags.mute_emails = True
    frappe.flags.in_seed = True

    try:
        _seed_bed_types()
        _seed_amenities()
        _seed_room_types()
        _seed_seasons()
        _seed_cancellation_policies()
        _seed_loyalty_programs()
        _seed_spa_services()
        _seed_event_venues()
        _seed_rate_plans()
        _seed_restaurants()
        _seed_settings_defaults()
        frappe.db.commit()
        print("✅ Velara seed data created successfully!")
    finally:
        frappe.flags.mute_emails = False
        frappe.flags.in_seed = False


# ---------------------------------------------------------------------------
# VL Bed Type — fields: bed_type_name (reqd), description
# ---------------------------------------------------------------------------
def _seed_bed_types():
    """Bed type reference data."""
    bed_types = [
        {"bed_type_name": "Single Bed", "description": "Standard single bed (90×200 cm)"},
        {"bed_type_name": "Double Bed", "description": "Standard double bed (140×200 cm)"},
        {"bed_type_name": "Queen Bed", "description": "Queen-size bed (160×200 cm)"},
        {"bed_type_name": "King Bed", "description": "King-size bed (180×200 cm)"},
        {"bed_type_name": "Twin Beds", "description": "Two single beds side by side"},
        {"bed_type_name": "Sofa Bed", "description": "Convertible sofa-bed for extra guests"},
        {"bed_type_name": "Bunk Bed", "description": "Stacked bunk beds (children/budget)"},
        {"bed_type_name": "Baby Cot", "description": "Portable baby cot on request"},
    ]

    for bt in bed_types:
        if not frappe.db.exists("VL Bed Type", bt["bed_type_name"]):
            frappe.get_doc({"doctype": "VL Bed Type", **bt}).insert(ignore_permissions=True)
            print(f"  🛏️ Bed Type: {bt['bed_type_name']}")


# ---------------------------------------------------------------------------
# VL Amenity — fields: amenity_name (reqd), amenity_type, icon,
#              is_chargeable, charge_amount
# ---------------------------------------------------------------------------
def _seed_amenities():
    """Room amenity reference data."""
    amenities = [
        # In-Room amenities
        {"amenity_name": "Wi-Fi", "amenity_type": "In-Room", "icon": "wifi"},
        {"amenity_name": "Air Conditioning", "amenity_type": "In-Room", "icon": "air-conditioning"},
        {"amenity_name": "Mini Bar", "amenity_type": "In-Room", "icon": "bottle",
         "is_chargeable": 1, "charge_amount": 0},
        {"amenity_name": "Safe Box", "amenity_type": "In-Room", "icon": "lock"},
        {"amenity_name": "Flat Screen TV", "amenity_type": "In-Room", "icon": "device-tv"},
        {"amenity_name": "Coffee Machine", "amenity_type": "In-Room", "icon": "coffee"},
        {"amenity_name": "Ironing Kit", "amenity_type": "In-Room", "icon": "iron"},
        # Bathroom
        {"amenity_name": "Hair Dryer", "amenity_type": "Bathroom", "icon": "scissors"},
        {"amenity_name": "Bathtub", "amenity_type": "Bathroom", "icon": "bath"},
        {"amenity_name": "Walk-in Shower", "amenity_type": "Bathroom", "icon": "droplet"},
        {"amenity_name": "Toiletries", "amenity_type": "Bathroom", "icon": "bottle"},
        # View
        {"amenity_name": "Sea View", "amenity_type": "View", "icon": "beach"},
        {"amenity_name": "City View", "amenity_type": "View", "icon": "building"},
        {"amenity_name": "Garden View", "amenity_type": "View", "icon": "tree"},
        {"amenity_name": "Pool View", "amenity_type": "View", "icon": "pool"},
        # Facility
        {"amenity_name": "Swimming Pool", "amenity_type": "Facility", "icon": "pool"},
        {"amenity_name": "Gym", "amenity_type": "Facility", "icon": "barbell"},
        {"amenity_name": "Spa Access", "amenity_type": "Facility", "icon": "yoga"},
        {"amenity_name": "Room Service", "amenity_type": "Facility", "icon": "bell-ringing"},
        {"amenity_name": "Parking", "amenity_type": "Facility", "icon": "parking"},
        {"amenity_name": "Airport Shuttle", "amenity_type": "Facility", "icon": "plane",
         "is_chargeable": 1, "charge_amount": 150},
        {"amenity_name": "Wheelchair Access", "amenity_type": "Facility", "icon": "wheelchair"},
    ]

    for am in amenities:
        if not frappe.db.exists("VL Amenity", am["amenity_name"]):
            frappe.get_doc({"doctype": "VL Amenity", **am}).insert(ignore_permissions=True)
            print(f"  🏨 Amenity: {am['amenity_name']}")


# ---------------------------------------------------------------------------
# VL Room Type — fields: room_type_name (reqd), room_type_code, description,
#                default_rate (reqd), max_occupancy, extra_bed_capacity,
#                base_bed_type (Link VL Bed Type), amenities (Table), image
# ---------------------------------------------------------------------------
def _seed_room_types():
    """Standard hotel room type templates."""
    room_types = [
        {"room_type_name": "Standard Single", "room_type_code": "STD-S",
         "default_rate": 250, "max_occupancy": 1, "extra_bed_capacity": 0,
         "base_bed_type": "Single Bed",
         "description": "Comfortable single room with essential amenities"},
        {"room_type_name": "Standard Double", "room_type_code": "STD-D",
         "default_rate": 400, "max_occupancy": 2, "extra_bed_capacity": 1,
         "base_bed_type": "Double Bed",
         "description": "Spacious double room for couples or business travelers"},
        {"room_type_name": "Superior Double", "room_type_code": "SUP-D",
         "default_rate": 550, "max_occupancy": 2, "extra_bed_capacity": 1,
         "base_bed_type": "Queen Bed",
         "description": "Enhanced room with premium amenities and better view"},
        {"room_type_name": "Deluxe Suite", "room_type_code": "DLX",
         "default_rate": 850, "max_occupancy": 3, "extra_bed_capacity": 1,
         "base_bed_type": "King Bed",
         "description": "Luxurious suite with separate living area"},
        {"room_type_name": "Family Room", "room_type_code": "FAM",
         "default_rate": 650, "max_occupancy": 4, "extra_bed_capacity": 2,
         "base_bed_type": "Twin Beds",
         "description": "Spacious room designed for families with children"},
        {"room_type_name": "Executive Suite", "room_type_code": "EXE",
         "default_rate": 1200, "max_occupancy": 2, "extra_bed_capacity": 1,
         "base_bed_type": "King Bed",
         "description": "Premium suite with business lounge access"},
        {"room_type_name": "Presidential Suite", "room_type_code": "PRES",
         "default_rate": 2500, "max_occupancy": 4, "extra_bed_capacity": 2,
         "base_bed_type": "King Bed",
         "description": "The finest accommodation with panoramic views"},
        {"room_type_name": "Accessible Room", "room_type_code": "ACC",
         "default_rate": 400, "max_occupancy": 2, "extra_bed_capacity": 0,
         "base_bed_type": "Double Bed",
         "description": "Wheelchair accessible room with adapted facilities"},
    ]

    for rt in room_types:
        if not frappe.db.exists("VL Room Type", rt["room_type_name"]):
            frappe.get_doc({"doctype": "VL Room Type", **rt}).insert(ignore_permissions=True)
            print(f"  🏠 Room Type: {rt['room_type_name']}")


# ---------------------------------------------------------------------------
# VL Season — fields: season_name (reqd), start_date (reqd), end_date (reqd),
#             rate_multiplier (reqd), is_active, color
# ---------------------------------------------------------------------------
def _seed_seasons():
    """Hotel pricing seasons with date ranges."""
    today = getdate(nowdate())
    year = today.year

    seasons = [
        {"season_name": "Peak Season", "start_date": f"{year}-06-15",
         "end_date": f"{year}-09-15", "rate_multiplier": 1.5, "is_active": 1,
         "color": "#e74c3c"},
        {"season_name": "Shoulder Season", "start_date": f"{year}-03-15",
         "end_date": f"{year}-06-14", "rate_multiplier": 1.2, "is_active": 1,
         "color": "#f39c12"},
        {"season_name": "Low Season", "start_date": f"{year}-11-01",
         "end_date": f"{year+1}-02-28", "rate_multiplier": 0.8, "is_active": 1,
         "color": "#3498db"},
        {"season_name": "Festival Season", "start_date": f"{year}-12-20",
         "end_date": f"{year+1}-01-05", "rate_multiplier": 1.8, "is_active": 1,
         "color": "#9b59b6"},
        {"season_name": "Ramadan", "start_date": f"{year}-03-01",
         "end_date": f"{year}-03-30", "rate_multiplier": 1.3, "is_active": 0,
         "color": "#27ae60"},
        {"season_name": "Hajj Season", "start_date": f"{year}-06-01",
         "end_date": f"{year}-06-20", "rate_multiplier": 2.0, "is_active": 0,
         "color": "#e67e22"},
    ]

    for s in seasons:
        if not frappe.db.exists("VL Season", s["season_name"]):
            frappe.get_doc({"doctype": "VL Season", **s}).insert(ignore_permissions=True)
            print(f"  📅 Season: {s['season_name']}")


# ---------------------------------------------------------------------------
# VL Cancellation Policy — fields: policy_name (reqd), hours_before,
#                          charge_type, charge_value, description
# ---------------------------------------------------------------------------
def _seed_cancellation_policies():
    """Standard cancellation policies."""
    policies = [
        {"policy_name": "Flexible", "hours_before": 24,
         "charge_type": "Percentage", "charge_value": 0,
         "description": "Free cancellation up to 24 hours before check-in"},
        {"policy_name": "Moderate", "hours_before": 48,
         "charge_type": "Percentage", "charge_value": 50,
         "description": "50% charge if cancelled within 48 hours"},
        {"policy_name": "Strict", "hours_before": 72,
         "charge_type": "Percentage", "charge_value": 100,
         "description": "Full charge if cancelled within 72 hours"},
        {"policy_name": "Non-Refundable", "hours_before": 0,
         "charge_type": "Percentage", "charge_value": 100,
         "description": "No refund upon cancellation at any time"},
    ]

    for p in policies:
        if not frappe.db.exists("VL Cancellation Policy", p["policy_name"]):
            frappe.get_doc({"doctype": "VL Cancellation Policy", **p}).insert(ignore_permissions=True)
            print(f"  📋 Policy: {p['policy_name']}")


# ---------------------------------------------------------------------------
# VL Loyalty Program — fields: program_name (reqd), is_active,
#     points_per_currency, silver_threshold, gold_threshold,
#     platinum_threshold, diamond_threshold,
#     silver_discount, gold_discount, platinum_discount, diamond_discount
# ---------------------------------------------------------------------------
def _seed_loyalty_programs():
    """Default loyalty program with tier thresholds."""
    prog_name = "Velara Rewards"
    if not frappe.db.exists("VL Loyalty Program", prog_name):
        frappe.get_doc({
            "doctype": "VL Loyalty Program",
            "program_name": prog_name,
            "is_active": 1,
            "points_per_currency": 1.0,
            "silver_threshold": 500,
            "gold_threshold": 2000,
            "platinum_threshold": 5000,
            "diamond_threshold": 15000,
            "silver_discount": 5,
            "gold_discount": 10,
            "platinum_discount": 15,
            "diamond_discount": 20,
        }).insert(ignore_permissions=True)
        print(f"  ⭐ Loyalty: {prog_name}")


# ---------------------------------------------------------------------------
# VL Spa Service — fields: service_name (reqd), service_type, duration_minutes,
#                  rate, is_active, description
# ---------------------------------------------------------------------------
def _seed_spa_services():
    """Spa service templates."""
    services = [
        {"service_name": "Swedish Massage", "service_type": "Massage",
         "duration_minutes": 60, "rate": 350, "is_active": 1,
         "description": "Classic relaxation massage using long flowing strokes"},
        {"service_name": "Deep Tissue Massage", "service_type": "Massage",
         "duration_minutes": 60, "rate": 400, "is_active": 1,
         "description": "Intense massage targeting deep muscle layers"},
        {"service_name": "Hot Stone Therapy", "service_type": "Massage",
         "duration_minutes": 90, "rate": 500, "is_active": 1,
         "description": "Heated basalt stones placed on key muscle groups"},
        {"service_name": "Facial Treatment", "service_type": "Facial",
         "duration_minutes": 45, "rate": 300, "is_active": 1,
         "description": "Cleansing, exfoliation, and hydration facial"},
        {"service_name": "Body Scrub", "service_type": "Body",
         "duration_minutes": 45, "rate": 250, "is_active": 1,
         "description": "Full-body exfoliation with natural ingredients"},
        {"service_name": "Aromatherapy", "service_type": "Massage",
         "duration_minutes": 60, "rate": 380, "is_active": 1,
         "description": "Essential oil massage for relaxation and wellbeing"},
        {"service_name": "Couples Massage", "service_type": "Massage",
         "duration_minutes": 90, "rate": 700, "is_active": 1,
         "description": "Side-by-side massage for two guests"},
        {"service_name": "Turkish Bath", "service_type": "Bath",
         "duration_minutes": 120, "rate": 450, "is_active": 1,
         "description": "Traditional hammam experience with steam and scrub"},
        {"service_name": "Moroccan Bath", "service_type": "Bath",
         "duration_minutes": 120, "rate": 500, "is_active": 1,
         "description": "Authentic Moroccan bathing ritual with black soap"},
    ]

    for s in services:
        if not frappe.db.exists("VL Spa Service", s["service_name"]):
            frappe.get_doc({"doctype": "VL Spa Service", **s}).insert(ignore_permissions=True)
            print(f"  💆 Spa: {s['service_name']}")


# ---------------------------------------------------------------------------
# VL Event Venue — fields: venue_name (reqd), property, venue_type,
#     capacity_theater, capacity_banquet, capacity_classroom,
#     capacity_boardroom, area_sqm, hourly_rate, daily_rate, image
# ---------------------------------------------------------------------------
def _seed_event_venues():
    """Standard event venue types (no property link — demo.py will handle that)."""
    venues = [
        {"venue_name": "Grand Ballroom", "venue_type": "Ballroom",
         "capacity_theater": 400, "capacity_banquet": 250,
         "capacity_classroom": 200, "capacity_boardroom": 80,
         "area_sqm": 600, "hourly_rate": 2000, "daily_rate": 12000},
        {"venue_name": "Beach Terrace", "venue_type": "Outdoor",
         "capacity_theater": 200, "capacity_banquet": 150,
         "capacity_classroom": 0, "capacity_boardroom": 0,
         "area_sqm": 400, "hourly_rate": 1500, "daily_rate": 8000},
        {"venue_name": "Meeting Room A", "venue_type": "Meeting Room",
         "capacity_theater": 60, "capacity_banquet": 40,
         "capacity_classroom": 30, "capacity_boardroom": 20,
         "area_sqm": 80, "hourly_rate": 500, "daily_rate": 3000},
        {"venue_name": "Meeting Room B", "venue_type": "Meeting Room",
         "capacity_theater": 40, "capacity_banquet": 25,
         "capacity_classroom": 20, "capacity_boardroom": 15,
         "area_sqm": 50, "hourly_rate": 350, "daily_rate": 2000},
        {"venue_name": "Lobby Lounge", "venue_type": "Lounge",
         "capacity_theater": 0, "capacity_banquet": 80,
         "capacity_classroom": 0, "capacity_boardroom": 0,
         "area_sqm": 200, "hourly_rate": 800, "daily_rate": 5000},
    ]

    for v in venues:
        if not frappe.db.exists("VL Event Venue", v["venue_name"]):
            frappe.get_doc({"doctype": "VL Event Venue", **v}).insert(ignore_permissions=True)
            print(f"  🎪 Venue: {v['venue_name']}")


# ---------------------------------------------------------------------------
# VL Rate Plan — fields: rate_plan_name (reqd), rate_plan_code, description,
#     meal_plan, is_refundable, cancellation_policy, base_rate_type,
#     fixed_rate, multiplier
# ---------------------------------------------------------------------------
def _seed_rate_plans():
    """Standard rate plans."""
    plans = [
        {"rate_plan_name": "Best Available Rate", "rate_plan_code": "BAR",
         "meal_plan": "Room Only", "is_refundable": 1,
         "cancellation_policy": "Flexible", "base_rate_type": "Multiplier",
         "multiplier": 1.0, "description": "Standard flexible rate"},
        {"rate_plan_name": "Bed and Breakfast", "rate_plan_code": "BB",
         "meal_plan": "Bed and Breakfast", "is_refundable": 1,
         "cancellation_policy": "Moderate", "base_rate_type": "Multiplier",
         "multiplier": 1.15, "description": "Room rate including daily breakfast"},
        {"rate_plan_name": "Half Board", "rate_plan_code": "HB",
         "meal_plan": "Half Board", "is_refundable": 1,
         "cancellation_policy": "Moderate", "base_rate_type": "Multiplier",
         "multiplier": 1.35, "description": "Breakfast and dinner included"},
        {"rate_plan_name": "Full Board", "rate_plan_code": "FB",
         "meal_plan": "Full Board", "is_refundable": 1,
         "cancellation_policy": "Strict", "base_rate_type": "Multiplier",
         "multiplier": 1.55, "description": "All three meals included"},
        {"rate_plan_name": "Non-Refundable Saver", "rate_plan_code": "NR",
         "meal_plan": "Room Only", "is_refundable": 0,
         "cancellation_policy": "Non-Refundable", "base_rate_type": "Multiplier",
         "multiplier": 0.85, "description": "15% discount, non-refundable"},
        {"rate_plan_name": "Corporate Rate", "rate_plan_code": "CORP",
         "meal_plan": "Bed and Breakfast", "is_refundable": 1,
         "cancellation_policy": "Flexible", "base_rate_type": "Multiplier",
         "multiplier": 0.80, "description": "Negotiated corporate rate"},
    ]

    for p in plans:
        if not frappe.db.exists("VL Rate Plan", p["rate_plan_name"]):
            frappe.get_doc({"doctype": "VL Rate Plan", **p}).insert(ignore_permissions=True)
            print(f"  💰 Rate Plan: {p['rate_plan_name']}")


# ---------------------------------------------------------------------------
# VL Restaurant — fields: restaurant_name (reqd), property, cuisine_type,
#     capacity, opening_time, closing_time, is_room_service, pos_profile
# ---------------------------------------------------------------------------
def _seed_restaurants():
    """Standard restaurant outlets (no property link — demo.py will set that)."""
    restaurants = [
        {"restaurant_name": "The Azure Restaurant", "cuisine_type": "International",
         "capacity": 120, "opening_time": "07:00", "closing_time": "23:00",
         "is_room_service": 0},
        {"restaurant_name": "Coral Café", "cuisine_type": "Café",
         "capacity": 60, "opening_time": "06:00", "closing_time": "22:00",
         "is_room_service": 0},
        {"restaurant_name": "Al Diwan", "cuisine_type": "Arabic",
         "capacity": 80, "opening_time": "12:00", "closing_time": "00:00",
         "is_room_service": 0},
        {"restaurant_name": "Room Service", "cuisine_type": "International",
         "capacity": 0, "opening_time": "06:00", "closing_time": "02:00",
         "is_room_service": 1},
    ]

    for r in restaurants:
        if not frappe.db.exists("VL Restaurant", r["restaurant_name"]):
            frappe.get_doc({"doctype": "VL Restaurant", **r}).insert(ignore_permissions=True)
            print(f"  🍽️ Restaurant: {r['restaurant_name']}")


# ---------------------------------------------------------------------------
# VL Settings defaults
# ---------------------------------------------------------------------------
def _seed_settings_defaults():
    """Set sensible defaults in VL Settings."""
    try:
        settings = frappe.get_single("VL Settings")
        if not settings.default_check_in_time:
            settings.default_check_in_time = "14:00:00"
        if not settings.default_check_out_time:
            settings.default_check_out_time = "12:00:00"
        if not settings.night_audit_time:
            settings.night_audit_time = "02:00:00"
        # Enable all modules by default
        for field in ["rooms_enabled", "reservations_enabled", "front_desk_enabled",
                      "housekeeping_enabled", "fnb_enabled", "revenue_enabled",
                      "guest_services_enabled", "events_enabled", "maintenance_enabled",
                      "loyalty_enabled", "night_audit_enabled", "spa_enabled"]:
            if hasattr(settings, field) and not getattr(settings, field):
                setattr(settings, field, 1)
        settings.save(ignore_permissions=True)
        print("  ⚙️ VL Settings defaults configured")
    except Exception as e:
        print(f"  ⚠️ Could not set VL Settings defaults: {e}")
