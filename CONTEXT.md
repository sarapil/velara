# VELARA — Hotel Management System

## Overview
VELARA (VL) is a comprehensive hotel management application built on Frappe/ERPNext v16.
It covers the full hotel operation lifecycle from reservations to checkout, with deep ERP integration.

## Architecture

### Modules (15)
| Module | Purpose |
|--------|---------|
| Velara | Root module |
| Velara Setup | Settings, Property, Room Types, Amenities, Seasons |
| Velara Rooms | Room management, floor plans, status tracking |
| Velara Reservations | Bookings, rate plans, group bookings, cancellation |
| Velara Front Desk | Guest profiles, folios, check-in/out |
| Velara Housekeeping | HK tasks, assignments, lost & found |
| Velara Food and Beverage | Restaurants, minibar, room service |
| Velara Revenue | Revenue budgets, forecasting |
| Velara Guest Services | Service requests, feedback, wake-up calls |
| Velara Events | Venues, event bookings |
| Velara Maintenance | Work orders, preventive maintenance |
| Velara Loyalty | Loyalty programs, point transactions |
| Velara Night Audit | Daily audit with KPIs (ADR, RevPAR, occupancy) |
| Velara Spa | Spa services and bookings |
| Velara Reports | Custom hotel reports |

### DocTypes (38 total)
**Setup (9):** VL Settings¹, VL Property, VL Room Type, VL Bed Type, VL Amenity,
VL Room Type Amenity², VL Season, VL Floor, VL Wing

**Rooms (3):** VL Room, VL Room Block, VL Room Status Log

**Reservations (4):** VL Reservation³, VL Group Booking, VL Cancellation Policy, VL Rate Plan

**Front Desk (5):** VL Guest, VL Folio³, VL Folio Charge², VL Check In³, VL Check Out³

**Housekeeping (3):** VL HK Task, VL HK Assignment, VL Lost and Found

**Guest Services (3):** VL Service Request, VL Guest Feedback, VL Wake Up Call

**Events (2):** VL Event Venue, VL Event Booking

**Maintenance (2):** VL Maintenance Request, VL Preventive Schedule

**F&B (3):** VL Restaurant, VL Minibar Consumption, VL Minibar Item²

**Loyalty (2):** VL Loyalty Program¹, VL Loyalty Transaction

**Night Audit (1):** VL Night Audit³

**Spa (2):** VL Spa Service, VL Spa Booking

**Revenue (1):** VL Revenue Budget

¹ Singleton  ² Child table  ³ Submittable

### Roles (14)
Velara Admin, Velara General Manager, Velara Front Desk Manager,
Velara Front Desk Agent, Velara Housekeeping Manager, Velara Housekeeper,
Velara Revenue Manager, Velara FnB Manager, Velara Concierge,
Velara Maintenance Tech, Velara Events Coordinator, Velara Spa Manager,
Velara Night Auditor, Velara Viewer

### ERPNext Integration
- **Customer** → VL Guest sync (bidirectional)
- **Sales Invoice** → VL Folio posting
- **Payment Entry** → Folio settlement
- **POS Invoice** → Post-to-Room feature
- **Item/Stock** → Minibar & amenity inventory
- **Employee** → Hotel department assignment
- **Asset** → Hotel equipment tracking

### Key APIs
| Endpoint | Purpose |
|----------|---------|
| `velara.api.dashboard.*` | Dashboard stats, occupancy trends |
| `velara.api.reservation.*` | Availability check, rate quotes, quick booking |
| `velara.api.room.*` | Room status changes, floor map |
| `velara.api.guest.*` | 360° guest profile, search |
| `velara.api.visual.*` | Graph data for frappe_visual components |
| `velara.api.user_management.*` | Staff & role management |

### Scheduled Tasks
- **Cron 2:00 AM:** Night audit
- **Cron */10min:** Room status updates
- **Cron */30min:** Reservation deadline checks
- **Daily:** Arrival/departure lists, maintenance schedules, HK auto-assign, loyalty processing
- **Hourly:** Channel rate sync, occupancy forecast, folio credit limits
- **Weekly:** Weekly reports, occupancy forecasting, group booking reminders
- **Monthly:** Revenue reports, loyalty tier recalculation, preventive maintenance

### Frontend
- **velara_boot.js** — Global namespace, utility functions, list view formatters
- **velara-variables.css** — CSS custom properties (gold/navy theme)
- **7 ERPNext extensions** — Customer, Sales Invoice, Payment Entry, Employee, Stock Entry, POS Invoice, Asset

### Brand
- **Colors:** Gold `#C9A84C` + Navy `#1B2A4A`
- **Logo:** Animated SVG (512×512) with hotel building, gold star, window glow
- **Desktop Icon:** 54×54 solid + subtle variants
- **CSS Variable Prefix:** `--vl-*`

## File Structure
```
velara/
├── __init__.py
├── hooks.py                    # App configuration
├── boot.py                     # Session boot data
├── install.py                  # Post-install setup
├── uninstall.py                # Cleanup
├── tasks.py                    # Scheduled tasks
├── notifications.py            # Notification config
├── utils.py                    # Core utilities
├── api/                        # Whitelisted APIs
│   ├── dashboard.py
│   ├── reservation.py
│   ├── room.py
│   ├── guest.py
│   ├── visual.py
│   ├── user_management.py
│   └── permissions.py
├── events/                     # ERPNext doc_events
│   ├── customer_events.py
│   ├── sales_invoice_events.py
│   ├── payment_events.py
│   ├── pos_events.py
│   ├── stock_events.py
│   └── employee_events.py
├── overrides/
│   └── customer_dashboard.py
├── velara_setup/doctype/       # 9 DocTypes
├── velara_rooms/doctype/       # 3 DocTypes
├── velara_reservations/doctype/ # 4 DocTypes
├── velara_front_desk/doctype/  # 5 DocTypes
├── velara_housekeeping/doctype/ # 3 DocTypes
├── velara_guest_services/doctype/ # 3 DocTypes
├── velara_events/doctype/      # 2 DocTypes
├── velara_maintenance/doctype/ # 2 DocTypes
├── velara_food_and_beverage/doctype/ # 3 DocTypes
├── velara_loyalty/doctype/     # 2 DocTypes
├── velara_night_audit/doctype/ # 1 DocType
├── velara_spa/doctype/         # 2 DocTypes
├── velara_revenue/doctype/     # 1 DocType
├── public/
│   ├── js/velara_boot.js
│   ├── js/extensions/          # 7 ERPNext form extensions
│   ├── css/velara-variables.css
│   └── images/velara-logo.svg
└── translations/               # AR + EN
```
