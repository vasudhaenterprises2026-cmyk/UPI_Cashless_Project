# SRS & SHREEM BUSINESS OS

## 1. Architecture overview

The application is designed as a multi-tenant business operating system for two entities under common ownership:

- SRS Enterprises (manufacturing + loose batter sales)
- Shreem S.M Food (branded packaged batter operations)

The system is implemented as a secure, transactional core backed by Supabase Postgres + Row Level Security, with Flutter on the frontend and n8n for orchestration and scheduled workflows.

### Recommended stack

- Frontend: Flutter + Dart
- Authentication: Supabase Auth
- Database: PostgreSQL via Supabase
- Backend: Supabase Edge Functions / secure Postgres functions / server-side business logic
- Workflow automation: n8n
- Reporting: XLSX/CSV exports and optional Microsoft Graph integration
- Notifications: in-app first, email/WhatsApp later

### Core principles

- Separate legal entity records for SRS and Shreem
- Internal transfers are not customer sales
- Inventory movement and financial entries are transactional and auditable
- Authorization is enforced server-side; UI access is only a convenience
- Sensitive financial and operational actions require explicit approval workflows

## 2. Module map

### 2.1 Authentication and access

- `profiles` - extended user profile data
- `user_business_roles` - role assignments by business
- `permissions` - role-to-permission mapping
- `audit_logs` - who did what, when, and why

### 2.2 Business setup

- `businesses` - SRS Enterprises and Shreem S.M Food
- `business_settings` - operational defaults, financial rules, stock alerts

### 2.3 Product and pricing management

- `products` - product catalog by business
- `product_variants` - pack sizes, units, product categories
- `product_prices` - effective prices by shop, product, and date range

### 2.4 Shop and customer master data

- `shops` - customer location records
- `shop_assignments` - assigned sales representatives
- `shop_prices` - agreed prices and effective dates
- `orders` / `order_lines` / `invoices` - sales lifecycle

### 2.5 Manufacturing and production

- `recipes` / `recipe_lines`
- `production_batches`
- `production_batch_items`
- `quality_checks`
- `batch_releases`

### 2.6 Inventory control

- `inventory_locations`
- `inventory_movements`
- `inventory_balances`
- `stock_adjustments`
- `inventory_transfers`

### 2.7 Financial operations

- `expenses`
- `payments`
- `payment_allocations`
- `ledgers`
- `receivables` / `payables`

### 2.8 Field operations and employee management

- `employees`
- `visit_plans`
- `shop_visits`
- `follow_ups`
- `attendance`

## 3. Database schema (Phase 1)

This implementation is intentionally a production-oriented schema foundation rather than a prototype-only spreadsheet model.

### Core data model summary

1. `businesses`
   - id
   - name
   - code
   - type
   - active
   - created_at

2. `users` / `profiles`
   - id references auth.users
   - full_name
   - phone
   - business_id
   - role(s)
   - active

3. `products`
   - id
   - business_id
   - name
   - category
   - unit_of_measure
   - pack_size
   - is_packaged_product
   - status

4. `product_prices`
   - id
   - shop_id
   - product_id
   - unit_price
   - valid_from
   - valid_to
   - source

5. `shops`
   - id
   - business_id
   - name
   - address
   - area
   - contact_name
   - phone
   - assigned_salesperson_id
   - status

6. `inventory_locations`
   - id
   - business_id
   - name
   - type
   - active

7. `inventory_movements`
   - id
   - business_id
   - location_id
   - product_id
   - movement_type
   - quantity
   - unit_cost
   - reference_type
   - reference_id
   - created_by
   - created_at

8. `orders`
   - id
   - business_id
   - shop_id
   - status
   - ordered_at
   - approved_by
   - total_amount

9. `order_lines`
   - id
   - order_id
   - product_id
   - quantity
   - unit_price
   - discount_amount
   - tax_amount
   - total_amount

10. `invoices`
   - id
   - order_id
   - business_id
   - invoice_number
   - total_amount
   - status

11. `expenses`
   - id
   - business_id
   - category
   - amount
   - incurred_on
   - vendor
   - payment_method
   - status

12. `audit_logs`
   - id
   - business_id
   - entity_type
   - entity_id
   - action
   - actor_id
   - payload
   - created_at

## 4. Authorization model

Role-based rules:

- OWNER / SUPER ADMIN: full access to both businesses and all modules
- PRODUCTION MANAGER: manufacturing and raw material workflows
- MARKETING EMPLOYEE: assigned shops, orders, visits, and follow-ups
- DELIVERY EMPLOYEE: dispatch, deliveries, discrepancy, and returns
- ACCOUNTANT: invoices, expenses, payables, receivables, and reconciliations

Important requirement: authorization checks must happen on the server side, not only in the UI. All sensitive transactions are validated in database functions and Postgres policies.

## 5. Data integrity constraints

The application is designed to prevent the most common operational failures:

- No duplicate inventory movement records for the same reference event
- No negative stock by default
- Internal business transfer is tracked as transfer, not external sale
- Historical prices remain tied to invoice/order time
- Financial entries are reversible, not deleted outright
- Audit logs are append-only

## 6. Production readiness notes

This repository was originally a Streamlit UPI data-analysis prototype. That project is not being replaced; instead, this folder provides the new business-OS foundation in a separate area so the original project remains intact.

The next engineering steps are:

- implement the full Supabase RLS policy set
- add the transactional SQL functions and triggers
- complete the Flutter app shell for all roles
- add CSV/XLSX validation and import preview
- configure n8n scheduled workflow triggers
- add test coverage for calculations, stock movement logic, and access control

## 7. Phase 1 implementation status

Implemented in this repository:

- architecture specification
- Phase 1 SQL schema
- secure role model foundation
- Flutter login + owner dashboard starter UI

Not yet implemented (planned in subsequent phases):

- full manufacturing, inventory, and sales workflows
- payment and invoice automation
- delivery and field marketing flows
- monthly report generation and Excel integration
- external automation via n8n

## 8. Summary

This is the correct production-oriented architecture for the SRS & SHREEM BUSINESS OS because it separates business ownership, creates a governed ledger, uses transactional backend logic, and supports role-aware reporting across both entities under one owner.
