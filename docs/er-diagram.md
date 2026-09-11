# FarmDirect Entity Relationship Diagram

## Overview

This document represents the database structure of the FarmDirect
platform.

The ERD shows the major entities, their attributes, primary keys,
foreign keys, relationships, and cardinality.

The design is based on the database schema defined in Issue #7.

Based on issue 7 design, ERD contain:
USERS
FARMER_PROFILES
FPO_PROFILES
PRODUCTS
INVENTORY
ORDERS
ORDER_ITEMS
BULK_REQUIREMENTS
OFFERS
PAYMENTS
REVIEWS

USERS
 │
 ├── FARMER_PROFILES
 │
 ├── FPO_PROFILES
 │
 ├── PRODUCTS
 │
 ├── ORDERS
 │
 ├── BULK_REQUIREMENTS
 │
 ├── OFFERS
 │
 └── REVIEWS

PRODUCTS
 │
 └── INVENTORY

ORDERS
 │
 ├── ORDER_ITEMS
 │
 └── PAYMENTS

PRODUCTS
 │
 └── ORDER_ITEMS

BULK_REQUIREMENTS
 │
 └── OFFERS

PRODUCTS
 │
 └── REVIEWS

USERS 1 ───────< PRODUCTS

USERS 1 ───────< ORDERS

ORDERS 1 ───────< ORDER_ITEMS

PRODUCTS 1 ───────< ORDER_ITEMS

BULK_REQUIREMENTS 1 ───────< OFFERS

USERS 1 ───────< OFFERS

PRODUCTS 1 ─────── 1 INVENTORY

## Relationships

| Relationship | Cardinality | Description |
|---|---|---|
| Users → Farmer Profiles | 1:0..1 | A farmer user can have one farmer profile. |
| Users → FPO Profiles | 1:0..1 | An FPO user can have one FPO profile. |
| Users → Products | 1:N | A producer can list multiple products. |
| Products → Inventory | 1:1 | Each product has an inventory record. |
| Users → Orders | 1:N | A buyer can place multiple orders. |
| Orders → Order Items | 1:N | An order can contain multiple items. |
| Products → Order Items | 1:N | A product can appear in multiple order items. |
| Users → Bulk Requirements | 1:N | A bulk buyer can create multiple requirements. |
| Bulk Requirements → Offers | 1:N | A requirement can receive multiple offers. |
| Users → Offers | 1:N | A producer can submit multiple offers. |
| Orders → Payments | 1:N | An order can have payment records. |
| Users → Reviews | 1:N | A user can write multiple reviews. |
| Products → Reviews | 1:N | A product can receive multiple reviews. |
| Orders → Reviews | 1:N | A review can be associated with an order. |

## Legend

- PK = Primary Key
- FK = Foreign Key
- UK = Unique Key
- 1:1 = One-to-one relationship
- 1:N = One-to-many relationship

USER
 │
 ├── Farmer → Farmer Profile
 ├── FPO → FPO Profile
 ├── Consumer
 ├── Bulk Buyer
 └── Administrator