# SRS & SHREEM BUSINESS OS

This folder contains the Phase 1 foundation for the SRS & SHREEM BUSINESS OS initiative.

It is intentionally kept separate from the existing repository's Streamlit prototype so the current project remains intact while the business system is scaffolded in a production-ready structure.

## Included in this Phase 1 foundation

- Architecture overview and implementation strategy
- PostgreSQL + Supabase schema for businesses, users, products, shops, and inventory
- Role-based permission model for owner, production manager, marketing employee, delivery employee, and accountant
- Flutter starter app with login and owner dashboard screens
- Phase 1 checklist aligned to the user requirements

## Key documents

- `ARCHITECTURE_AND_SCHEMA.md` — architecture, module map, and database schema
- `supabase/schema_phase1.sql` — PostgreSQL schema foundation for Phase 1
- `flutter/` — Flutter app skeleton for login, navigation, and dashboards

## Phase 1 scope implemented

- Business setup for SRS Enterprises and Shreem S.M Food
- Role model and access rules
- Product catalog and pack/unit differentiation
- Shop master data and pricing history
- Inventory and audit foundations
- Owner dashboard starter screen

## Next steps

- Implement Supabase auth and row-level security policies
- Add the app shell navigation for production manager, accountant, marketing, and delivery roles
- Add CSV/XLSX import preview and validation modules
- Create transactional inventory and sales APIs
- Add n8n workflow hooks and scheduled reports

## Run the Flutter starter app

From the `flutter` directory:

```bash
flutter pub get
flutter run
```

## Supabase setup

Apply the schema in `supabase/schema_phase1.sql` to a Supabase Postgres project before building the rest of the business workflows.
