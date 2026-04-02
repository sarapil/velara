"""
Velara Hotel Management — Demo Data
Creates a realistic sample hotel with rooms, guests, and reservations.
Depends on seed data (run seed.py first).

Usage:
    bench --site dev.localhost execute velara.setup.demo.run
"""

import frappe
from frappe.utils import nowdate, add_days, getdate, now_datetime
import random


def run():
    """Main entry point for creating Velara demo data."""
    frappe.flags.mute_emails = True
    frappe.flags.in_demo = True

    try:
        property_name = _create_demo_property()
        _create_demo_floors(property_name)
        _create_demo_rooms(property_name)
        _create_demo_guests()
        _create_demo_reservations(property_name)
        _create_demo_hk_tasks(property_name)
        _create_demo_maintenance_requests()
        _create_demo_minibar_consumptions()
        _create_demo_spa_bookings()
        _create_demo_event_bookings()
        frappe.db.commit()
        print("✅ Velara demo data created successfully!")
    finally:
        frappe.flags.mute_emails = False
        frappe.flags.in_demo = False


def _create_demo_property():
    """Create the demo hotel property."""
    prop_name = "Azure Bay Resort"
    if not frappe.db.exists("VL Property", prop_name):
        frappe.get_doc({
            "doctype": "VL Property",
            "property_name": prop_name,
            "property_code": "ABR",
            "company": frappe.db.get_single_value("Global Defaults", "default_company")
                       or frappe.db.get_value("Company", {}, "name"),
            "star_rating": "5",
            "property_type": "Resort",
            "total_rooms": 120,
            "address": "Corniche Road, Obhur District",
            "city": "Jeddah",
            "country": "Saudi Arabia",
            "phone": "+966 12 345 6789",
            "email": "info@azurebay.example.com",
            "website": "https://azurebay.example.com",
        }).insert(ignore_permissions=True)
        print(f"  🏨 Property: {prop_name}")
    return prop_name


def _create_demo_floors(property_name):
    """Create floors for the demo property."""
    floors = [
        {"floor_name": "Ground Floor", "floor_number": 0},
        {"floor_name": "1st Floor", "floor_number": 1},
        {"floor_name": "2nd Floor", "floor_number": 2},
        {"floor_name": "3rd Floor", "floor_number": 3},
        {"floor_name": "4th Floor", "floor_number": 4},
        {"floor_name": "5th Floor", "floor_number": 5},
    ]

    for f in floors:
        if not frappe.db.exists("VL Floor", f["floor_name"]):
            frappe.get_doc({
                "doctype": "VL Floor",
                "property": property_name,
                **f,
            }).insert(ignore_permissions=True)
            print(f"  🏢 Floor: {f['floor_name']}")


# (room_number, room_type, floor, room_status, housekeeping_status)
DEMO_ROOMS = [
    # 1st Floor — Standard rooms
    ("101", "Standard Single", "1st Floor", "Available", "Clean"),
    ("102", "Standard Single", "1st Floor", "Available", "Clean"),
    ("103", "Standard Double", "1st Floor", "Occupied", "Clean"),
    ("104", "Standard Double", "1st Floor", "Available", "Clean"),
    ("105", "Standard Double", "1st Floor", "Reserved", "Clean"),
    ("106", "Standard Single", "1st Floor", "Out of Order", "Clean"),
    ("107", "Standard Double", "1st Floor", "Available", "Clean"),
    ("108", "Standard Double", "1st Floor", "Available", "Clean"),
    # 2nd Floor — Superior rooms
    ("201", "Superior Double", "2nd Floor", "Available", "Clean"),
    ("202", "Superior Double", "2nd Floor", "Occupied", "Clean"),
    ("203", "Superior Double", "2nd Floor", "Available", "Clean"),
    ("204", "Standard Double", "2nd Floor", "Available", "Clean"),
    ("205", "Superior Double", "2nd Floor", "Reserved", "Clean"),
    ("206", "Standard Double", "2nd Floor", "Available", "Dirty"),
    ("207", "Superior Double", "2nd Floor", "Available", "Clean"),
    ("208", "Superior Double", "2nd Floor", "Available", "Clean"),
    # 3rd Floor — Deluxe
    ("301", "Deluxe Suite", "3rd Floor", "Available", "Clean"),
    ("302", "Deluxe Suite", "3rd Floor", "Occupied", "Clean"),
    ("303", "Deluxe Suite", "3rd Floor", "Available", "Clean"),
    ("304", "Deluxe Suite", "3rd Floor", "Available", "Clean"),
    # 4th Floor — Executive & Family
    ("401", "Executive Suite", "4th Floor", "Available", "Clean"),
    ("402", "Executive Suite", "4th Floor", "Occupied", "Clean"),
    ("403", "Family Room", "4th Floor", "Available", "Clean"),
    ("404", "Family Room", "4th Floor", "Reserved", "Clean"),
    # 5th Floor — Presidential
    ("501", "Presidential Suite", "5th Floor", "Available", "Clean"),
    ("502", "Presidential Suite", "5th Floor", "Available", "Clean"),
]


def _create_demo_rooms(property_name):
    """Create demo rooms across floors."""
    created = 0
    for room_no, room_type, floor, room_status, hk_status in DEMO_ROOMS:
        if not frappe.db.exists("VL Room", {"room_number": room_no, "property": property_name}):
            frappe.get_doc({
                "doctype": "VL Room",
                "room_number": room_no,
                "room_type": room_type,
                "property": property_name,
                "floor": floor,
                "room_status": room_status,
                "housekeeping_status": hk_status,
            }).insert(ignore_permissions=True)
            created += 1
    print(f"  🚪 Created {created} demo rooms")


# Demo guest data
DEMO_GUESTS = [
    {"first_name": "Ahmed", "last_name": "Al-Rashidi",
     "email": "ahmed.r@example.com", "mobile": "+966501112222",
     "nationality": "Saudi Arabia", "id_type": "National ID", "id_number": "1088776655",
     "gender": "Male"},
    {"first_name": "Sarah", "last_name": "Johnson",
     "email": "sarah.j@example.com", "mobile": "+15551234567",
     "nationality": "United States", "id_type": "Passport", "id_number": "US123456789",
     "gender": "Female", "vip_code": "VIP"},
    {"first_name": "Mohammed", "last_name": "Hassan",
     "email": "m.hassan@example.com", "mobile": "+966553334444",
     "nationality": "Saudi Arabia", "id_type": "National ID", "id_number": "1099887766",
     "gender": "Male"},
    {"first_name": "Emma", "last_name": "Weber",
     "email": "emma.w@example.com", "mobile": "+491705556666",
     "nationality": "Germany", "id_type": "Passport", "id_number": "DE987654321",
     "gender": "Female"},
    {"first_name": "Khalid", "last_name": "bin Salman",
     "email": "khalid.s@example.com", "mobile": "+966505556666",
     "nationality": "Saudi Arabia", "id_type": "National ID", "id_number": "1077665544",
     "gender": "Male", "vip_code": "VVIP"},
    {"first_name": "Fatima", "last_name": "Al-Zahra",
     "email": "fatima.z@example.com", "mobile": "+966557778888",
     "nationality": "Saudi Arabia", "id_type": "National ID", "id_number": "1066554433",
     "gender": "Female"},
    {"first_name": "John", "last_name": "Smith",
     "email": "john.s@example.com", "mobile": "+447700900123",
     "nationality": "United Kingdom", "id_type": "Passport", "id_number": "GB112233445",
     "gender": "Male"},
    {"first_name": "Yuki", "last_name": "Tanaka",
     "email": "yuki.t@example.com", "mobile": "+819012345678",
     "nationality": "Japan", "id_type": "Passport", "id_number": "JP998877665",
     "gender": "Female"},
    {"first_name": "Omar", "last_name": "Al-Farsi",
     "email": "omar.f@example.com", "mobile": "+96891112233",
     "nationality": "Oman", "id_type": "Passport", "id_number": "OM554433221",
     "gender": "Male"},
    {"first_name": "Maria", "last_name": "Garcia",
     "email": "maria.g@example.com", "mobile": "+34612345678",
     "nationality": "Spain", "id_type": "Passport", "id_number": "ES776655443",
     "gender": "Female"},
]


def _create_demo_guests():
    """Create sample guest profiles."""
    created = 0
    for g in DEMO_GUESTS:
        if not frappe.db.exists("VL Guest", {"email": g["email"]}):
            frappe.get_doc({"doctype": "VL Guest", **g}).insert(ignore_permissions=True)
            created += 1
    print(f"  👤 Created {created} demo guests")


def _get_guest(email):
    """Lookup guest by email, return name or None."""
    return frappe.db.get_value("VL Guest", {"email": email}, "name")


def _get_room_type_rate(room_type_name):
    """Get the default_rate for a room type."""
    return frappe.db.get_value("VL Room Type", room_type_name, "default_rate") or 0


def _create_demo_reservations(property_name):
    """Create sample reservations in various states."""
    today = getdate(nowdate())

    reservations = [
        # Currently checked-in (matching Occupied rooms)
        {"guest_email": "ahmed.r@example.com", "room": "103", "room_type": "Standard Double",
         "check_in": add_days(today, -2), "check_out": add_days(today, 3),
         "status": "Checked In", "booking_source": "Direct", "adults": 1},
        {"guest_email": "sarah.j@example.com", "room": "202", "room_type": "Superior Double",
         "check_in": add_days(today, -1), "check_out": add_days(today, 5),
         "status": "Checked In", "booking_source": "OTA", "adults": 2},
        {"guest_email": "m.hassan@example.com", "room": "302", "room_type": "Deluxe Suite",
         "check_in": add_days(today, -3), "check_out": add_days(today, 1),
         "status": "Checked In", "booking_source": "Direct", "adults": 2},
        {"guest_email": "khalid.s@example.com", "room": "402", "room_type": "Executive Suite",
         "check_in": today, "check_out": add_days(today, 7),
         "status": "Checked In", "booking_source": "Corporate", "adults": 1},
        # Upcoming (matching Reserved rooms)
        {"guest_email": "emma.w@example.com", "room": "105", "room_type": "Standard Double",
         "check_in": add_days(today, 1), "check_out": add_days(today, 4),
         "status": "Confirmed", "booking_source": "OTA", "adults": 2},
        {"guest_email": "fatima.z@example.com", "room": "205", "room_type": "Superior Double",
         "check_in": add_days(today, 2), "check_out": add_days(today, 6),
         "status": "Confirmed", "booking_source": "Direct", "adults": 1},
        {"guest_email": "john.s@example.com", "room": "404", "room_type": "Family Room",
         "check_in": add_days(today, 3), "check_out": add_days(today, 8),
         "status": "Confirmed", "booking_source": "Travel Agent", "adults": 2, "children": 2},
        # Future
        {"guest_email": "yuki.t@example.com", "room": "301", "room_type": "Deluxe Suite",
         "check_in": add_days(today, 7), "check_out": add_days(today, 14),
         "status": "Confirmed", "booking_source": "OTA", "adults": 2},
        {"guest_email": "omar.f@example.com", "room": "501", "room_type": "Presidential Suite",
         "check_in": add_days(today, 10), "check_out": add_days(today, 15),
         "status": "Confirmed", "booking_source": "Direct", "adults": 2},
        # Past completed
        {"guest_email": "maria.g@example.com", "room": "201", "room_type": "Superior Double",
         "check_in": add_days(today, -10), "check_out": add_days(today, -5),
         "status": "Checked Out", "booking_source": "OTA", "adults": 1},
    ]

    created = 0
    for r in reservations:
        guest = _get_guest(r["guest_email"])
        if not guest:
            continue
        rate = _get_room_type_rate(r["room_type"])
        nights = (getdate(r["check_out"]) - getdate(r["check_in"])).days
        existing = frappe.db.exists("VL Reservation", {
            "guest": guest, "check_in_date": r["check_in"],
        })
        if not existing:
            frappe.get_doc({
                "doctype": "VL Reservation",
                "guest": guest,
                "property": property_name,
                "room_type": r["room_type"],
                "room": r.get("room"),
                "check_in_date": r["check_in"],
                "check_out_date": r["check_out"],
                "nights": nights,
                "status": r["status"],
                "booking_source": r.get("booking_source", "Direct"),
                "room_rate": rate,
                "total_room_charges": rate * nights,
                "adults": r.get("adults", 1),
                "children": r.get("children", 0),
                "cancellation_policy": "Flexible",
            }).insert(ignore_permissions=True)
            created += 1
    print(f"  📋 Created {created} demo reservations")


def _create_demo_hk_tasks(property_name):
    """Create sample housekeeping tasks (VL HK Task)."""
    today = getdate(nowdate())

    tasks = [
        {"room": "206", "task_type": "Checkout Clean", "priority": "High",
         "status": "Pending"},
        {"room": "103", "task_type": "Stayover Clean", "priority": "Medium",
         "status": "In Progress"},
        {"room": "202", "task_type": "Stayover Clean", "priority": "Medium",
         "status": "Pending"},
        {"room": "301", "task_type": "Deep Clean", "priority": "Low",
         "status": "Pending"},
        {"room": "501", "task_type": "VIP Preparation", "priority": "Urgent",
         "status": "Pending"},
    ]

    created = 0
    for t in tasks:
        if not frappe.db.exists("VL HK Task", {
            "room": t["room"], "task_type": t["task_type"],
        }):
            frappe.get_doc({
                "doctype": "VL HK Task",
                "scheduled_date": today,
                **t,
            }).insert(ignore_permissions=True)
            created += 1
    print(f"  🧹 Created {created} housekeeping tasks")


def _create_demo_maintenance_requests():
    """Create sample maintenance requests (VL Maintenance Request)."""
    today = getdate(nowdate())

    requests = [
        {"room": "106", "description": "AC not cooling properly — compressor may need servicing",
         "priority": "High", "category": "HVAC", "status": "In Progress"},
        {"room": "204", "description": "Bathroom faucet leaking intermittently",
         "priority": "Medium", "category": "Plumbing", "status": "Open"},
        {"room": "303", "description": "TV remote control buttons unresponsive",
         "priority": "Low", "category": "Electronics", "status": "Open"},
    ]

    created = 0
    for r in requests:
        if not frappe.db.exists("VL Maintenance Request", {
            "room": r["room"], "description": r["description"],
        }):
            frappe.get_doc({
                "doctype": "VL Maintenance Request",
                "reported_date": today,
                **r,
            }).insert(ignore_permissions=True)
            created += 1
    print(f"  🔧 Created {created} maintenance requests")


def _create_demo_minibar_consumptions():
    """Create sample minibar charges (VL Minibar Consumption)."""
    today = getdate(nowdate())

    items = [
        {"room": "103", "consumption_date": today, "total_amount": 45},
        {"room": "302", "consumption_date": add_days(today, -1), "total_amount": 85},
        {"room": "402", "consumption_date": today, "total_amount": 60},
    ]

    created = 0
    for item in items:
        guest_link = frappe.db.get_value("VL Room", {"room_number": item["room"]}, "current_guest")
        if not frappe.db.exists("VL Minibar Consumption", {
            "room": item["room"], "consumption_date": item["consumption_date"],
        }):
            doc_data = {
                "doctype": "VL Minibar Consumption",
                "room": item["room"],
                "consumption_date": item["consumption_date"],
                "total_amount": item["total_amount"],
            }
            if guest_link:
                doc_data["guest"] = guest_link
            frappe.get_doc(doc_data).insert(ignore_permissions=True)
            created += 1
    print(f"  🥤 Created {created} minibar consumptions")


def _create_demo_spa_bookings():
    """Create sample spa bookings (VL Spa Booking)."""
    today = getdate(nowdate())

    bookings = [
        {"guest_email": "sarah.j@example.com", "spa_service": "Swedish Massage",
         "booking_datetime": f"{today} 10:00:00", "status": "Confirmed"},
        {"guest_email": "emma.w@example.com", "spa_service": "Facial Treatment",
         "booking_datetime": f"{add_days(today, 1)} 14:00:00", "status": "Confirmed"},
        {"guest_email": "fatima.z@example.com", "spa_service": "Moroccan Bath",
         "booking_datetime": f"{add_days(today, 2)} 11:00:00", "status": "Confirmed"},
        {"guest_email": "maria.g@example.com", "spa_service": "Couples Massage",
         "booking_datetime": f"{add_days(today, -7)} 16:00:00", "status": "Completed"},
    ]

    created = 0
    for b in bookings:
        guest = _get_guest(b["guest_email"])
        if not guest:
            continue
        rate = frappe.db.get_value("VL Spa Service", b["spa_service"], "rate") or 0
        if not frappe.db.exists("VL Spa Booking", {
            "guest": guest, "spa_service": b["spa_service"],
            "booking_datetime": b["booking_datetime"],
        }):
            frappe.get_doc({
                "doctype": "VL Spa Booking",
                "guest": guest,
                "spa_service": b["spa_service"],
                "booking_datetime": b["booking_datetime"],
                "status": b["status"],
                "charge_amount": rate,
            }).insert(ignore_permissions=True)
            created += 1
    print(f"  💆 Created {created} spa bookings")


def _create_demo_event_bookings():
    """Create sample event bookings (VL Event Booking)."""
    today = getdate(nowdate())

    events = [
        {"event_name": "Corporate Annual Dinner", "venue": "Grand Ballroom",
         "event_type": "Corporate",
         "start_datetime": f"{add_days(today, 5)} 19:00:00",
         "end_datetime": f"{add_days(today, 5)} 23:00:00",
         "guests_count": 200, "status": "Confirmed",
         "contact_person": "Ali Mahmoud", "contact_phone": "+966501234567",
         "total_amount": 25000, "deposit_amount": 10000},
        {"event_name": "Beach Wedding Reception", "venue": "Beach Terrace",
         "event_type": "Wedding",
         "start_datetime": f"{add_days(today, 14)} 17:00:00",
         "end_datetime": f"{add_days(today, 14)} 23:59:00",
         "guests_count": 150, "status": "Confirmed",
         "contact_person": "Nora Al-Saud", "contact_phone": "+966559876543",
         "total_amount": 35000, "deposit_amount": 15000},
        {"event_name": "Product Launch Seminar", "venue": "Meeting Room A",
         "event_type": "Conference",
         "start_datetime": f"{add_days(today, 3)} 09:00:00",
         "end_datetime": f"{add_days(today, 3)} 17:00:00",
         "guests_count": 50, "status": "Tentative",
         "contact_person": "James Clark", "contact_phone": "+447891234567",
         "total_amount": 5000, "deposit_amount": 2000},
        {"event_name": "Weekend Jazz Night", "venue": "Lobby Lounge",
         "event_type": "Entertainment",
         "start_datetime": f"{add_days(today, 7)} 20:00:00",
         "end_datetime": f"{add_days(today, 7)} 23:30:00",
         "guests_count": 80, "status": "Confirmed",
         "contact_person": "Hotel Events", "contact_phone": "+966123456789",
         "total_amount": 8000, "deposit_amount": 8000},
    ]

    created = 0
    for e in events:
        if not frappe.db.exists("VL Event Booking", {"event_name": e["event_name"]}):
            frappe.get_doc({"doctype": "VL Event Booking", **e}).insert(ignore_permissions=True)
            created += 1
    print(f"  🎉 Created {created} event bookings")
