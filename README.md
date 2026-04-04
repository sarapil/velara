# VELARA — Hotel & Hospitality Management System

<p align="center">
  <img src="velara/public/images/velara-logo-animated.svg" alt="VELARA Logo" width="160">
</p>

<h3 align="center">نظام إدارة الفنادق والضيافة</h3>

<p align="center">
  <a href="https://github.com/ArkanLab/velara/actions/workflows/ci.yml">
    <img src="https://github.com/ArkanLab/velara/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/ArkanLab/velara/actions/workflows/linters.yml">
    <img src="https://github.com/ArkanLab/velara/actions/workflows/linters.yml/badge.svg" alt="Linters">
  </a>
  <img src="https://img.shields.io/badge/Frappe-v16-blue" alt="Frappe v16">
  <img src="https://img.shields.io/badge/ERPNext-v16-green" alt="ERPNext v16">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
  <img src="https://img.shields.io/badge/i18n-Arabic%20%2B%2011%20languages-brightgreen" alt="Multilingual">
</p>

---

> Enterprise hotel property management system built on Frappe v16 + ERPNext, with full Arabic/RTL support and CAPS-based access control.

## ✨ Features

- 🏨 **Front Desk Operations** — Check-in/check-out, guest registration, room assignment, walk-in handling
- 📅 **Reservation Management** — Direct, OTA, corporate, and group booking workflows with rate plan engine
- 🛏️ **Room Inventory** — Room types, floor plans, amenities, maintenance tracking, housekeeping status
- 🍽️ **F&B Operations** — Restaurant outlets, menus, room service, banquet packages, kitchen integration
- 🎉 **Events & Banquets** — Event booking, venue management, catering coordination
- 💆 **Spa & Wellness** — Service scheduling, therapist management, package deals
- ⭐ **Guest Loyalty** — Tier-based loyalty program, points earning/redemption, member benefits
- 💰 **Revenue Management** — Dynamic pricing, rate plans, seasonal adjustments, yield analytics
- 🔧 **Maintenance** — Preventive/reactive maintenance, work orders, vendor management
- 🌙 **Night Audit** — Automated daily close, revenue posting, occupancy statistics
- 📊 **14 Workspaces** — Dedicated dashboards for each operational area
- 🌐 **Multilingual** — Arabic + English + 10 additional languages (Turkish, French, Urdu, Hindi, Persian, etc.)

## 📦 Installation

```bash
bench get-app https://github.com/ArkanLab/velara --branch main
bench --site <site_name> install-app velara
bench migrate
```

### Requirements

- Frappe Framework v16+
- ERPNext v16+
- HRMS v16+
- frappe_visual (UI component library)
- CAPS (access control)

## 🏗️ Architecture

| Module | DocTypes | Purpose |
|--------|----------|---------|
| Velara Setup | 15+ | Hotel properties, room types, rate plans, configurations |
| Front Desk | 10+ | Check-in/out, guest profiles, folio management |
| Reservations | 8+ | Bookings, availability, channel management |
| Rooms | 6+ | Inventory, housekeeping, maintenance status |
| F&B | 8+ | Restaurant, menu, orders, kitchen display |
| Events | 5+ | Banquets, venues, catering |
| Spa & Wellness | 4+ | Services, therapists, appointments |
| Loyalty | 4+ | Tiers, points, redemptions |
| Revenue | 6+ | Rate plans, yield, forecasting |
| Reports | 10+ | Occupancy, revenue, guest analytics |

## 🤝 Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/velara
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

## 🔄 CI

This app uses GitHub Actions for CI. The following workflows are configured:

- **CI:** Installs this app and runs unit tests on every push to `develop` branch
- **Linters:** Runs Ruff, Semgrep security rules, and ESLint on every pull request
- **Release:** Auto-creates GitHub Releases on `v*` tag push

## 📄 License

MIT
