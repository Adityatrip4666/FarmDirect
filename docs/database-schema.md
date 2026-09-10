# FarmDirect Database Schema

## 1. Overview

FarmDirect uses SQLite as the relational database for storing
application data.

The database supports users, farmer and FPO profiles, products,
inventory, orders, bulk buyer requirements, offers, payments,
and reviews.

The schema is designed to maintain data integrity through primary
keys, foreign keys, constraints, and defined relationships between
entities.

users
farmer_profiles
fpo_profiles
products
inventory
orders
order_items
bulk_requirements
offers
payments
reviews

| Field         | Data Type | Key    | Description                          |
| ------------- | --------- | ------ | ------------------------------------ |
| id            | INTEGER   | PK     | Unique user ID                       |
| name          | TEXT      |        | User's name                          |
| email         | TEXT      | UNIQUE | Login email                          |
| password_hash | TEXT      |        | Hashed password                      |
| role          | TEXT      |        | Farmer/FPO/Consumer/Bulk Buyer/Admin |
| phone         | TEXT      |        | Contact number                       |
| status        | TEXT      |        | Account status                       |
| created_at    | DATETIME  |        | Account creation time                |
| updated_at    | DATETIME  |        | Last update                          |


users
  │
  ├── farmer_profiles
  ├── fpo_profiles
  ├── products
  ├── orders
  ├── bulk_requirements
  ├── offers
  └── reviews

  Farmer → farmer_profiles
FPO → fpo_profiles
Consumer → orders
Bulk Buyer → bulk_requirements

| Field       | Data Type | Key | Description         |
| ----------- | --------- | --- | ------------------- |
| id          | INTEGER   | PK  | Farmer profile ID   |
| user_id     | INTEGER   | FK  | References users.id |
| farm_name   | TEXT      |     | Farm name           |
| location    | TEXT      |     | Farm location       |
| description | TEXT      |     | Farm information    |
| created_at  | DATETIME  |     | Creation time       |
| updated_at  | DATETIME  |     | Last update         |

users 1 ───── 1 farmer_profiles
users.id

| Field               | Data Type | Key | Description             |
| ------------------- | --------- | --- | ----------------------- |
| id                  | INTEGER   | PK  | FPO profile ID          |
| user_id             | INTEGER   | FK  | References users.id     |
| organization_name   | TEXT      |     | FPO name                |
| registration_number | TEXT      |     | Registration identifier |
| location            | TEXT      |     | Organization location   |
| description         | TEXT      |     | FPO information         |
| created_at          | DATETIME  |     | Creation time           |
| updated_at          | DATETIME  |     | Last update             |

users 1 ───── 1 fpo_profiles

| Field       | Data Type | Key | Description            |
| ----------- | --------- | --- | ---------------------- |
| id          | INTEGER   | PK  | Product ID             |
| seller_id   | INTEGER   | FK  | References users.id    |
| name        | TEXT      |     | Product name           |
| description | TEXT      |     | Product description    |
| category    | TEXT      |     | Product category       |
| unit        | TEXT      |     | kg, litre, piece, etc. |
| price       | DECIMAL   |     | Price per unit         |
| status      | TEXT      |     | Active/inactive        |
| created_at  | DATETIME  |     | Creation time          |
| updated_at  | DATETIME  |     | Last update            |

users 1 ───── * products

seller_id → users.id

| Field              | Data Type | Key | Description            |
| ------------------ | --------- | --- | ---------------------- |
| id                 | INTEGER   | PK  | Inventory record ID    |
| product_id         | INTEGER   | FK  | References products.id |
| quantity_available | DECIMAL   |     | Available quantity     |
| quantity_reserved  | DECIMAL   |     | Reserved quantity      |
| updated_at         | DATETIME  |     | Last inventory update  |

products 1 ───── 1 inventory

for example-
Tomatoes
Price: ₹40/kg

Inventory:
Available = 500 kg
Reserved = 50 kg

| Field            | Data Type | Key | Description                           |
| ---------------- | --------- | --- | ------------------------------------- |
| id               | INTEGER   | PK  | Order ID                              |
| buyer_id         | INTEGER   | FK  | References users.id                   |
| status           | TEXT      |     | Pending/Confirmed/Completed/Cancelled |
| total_amount     | DECIMAL   |     | Total order value                     |
| shipping_address | TEXT      |     | Delivery address                      |
| created_at       | DATETIME  |     | Order creation time                   |
| updated_at       | DATETIME  |     | Last update                           |

users 1 ───── * orders

for example-
Order #1001

Tomatoes    10 kg
Potatoes     5 kg
Onions       8 kg

| Field      | Data Type | Key | Description            |
| ---------- | --------- | --- | ---------------------- |
| id         | INTEGER   | PK  | Order item ID          |
| order_id   | INTEGER   | FK  | References orders.id   |
| product_id | INTEGER   | FK  | References products.id |
| quantity   | DECIMAL   |     | Ordered quantity       |
| unit_price | DECIMAL   |     | Price at time of order |
| subtotal   | DECIMAL   |     | Quantity × unit price  |


orders 1 ───── * order_items
products 1 ───── * order_items

| Field             | Data Type | Key | Description                |
| ----------------- | --------- | --- | -------------------------- |
| id                | INTEGER   | PK  | Requirement ID             |
| buyer_id          | INTEGER   | FK  | References users.id        |
| product_name      | TEXT      |     | Required product           |
| quantity_required | DECIMAL   |     | Required quantity          |
| target_price      | DECIMAL   |     | Optional target price      |
| delivery_location | TEXT      |     | Required delivery location |
| required_by       | DATE      |     | Required date              |
| status            | TEXT      |     | Open/Closed/Fulfilled      |
| created_at        | DATETIME  |     | Creation time              |
| updated_at        | DATETIME  |     | Last update                |


users 1 ───── * bulk_requirements

Bulk Buyer
     ↓
Needs 5,000 kg potatoes
     ↓
FarmDirect requirement
     ↓
Farmers/FPOs see requirement
     ↓
Farmers/FPOs submit offers


Design Offers

| Field          | Data Type | Key | Description                     |
| -------------- | --------- | --- | ------------------------------- |
| id             | INTEGER   | PK  | Offer ID                        |
| requirement_id | INTEGER   | FK  | References bulk_requirements.id |
| seller_id      | INTEGER   | FK  | References users.id             |
| quantity       | DECIMAL   |     | Offered quantity                |
| price          | DECIMAL   |     | Offered price                   |
| message        | TEXT      |     | Seller message                  |
| status         | TEXT      |     | Pending/Accepted/Rejected       |
| created_at     | DATETIME  |     | Offer creation time             |
| updated_at     | DATETIME  |     | Last update                     |

bulk_requirements 1 ───── * offers

users 1 ───── * offers

Bulk Buyer
   │
   │ creates
   ▼
Requirement
   │
   │ receives
   ▼
Offers
   ▲
   │
Farmers/FPOs


Design Payments

| Field                 | Data Type | Key    | Description                        |
| --------------------- | --------- | ------ | ---------------------------------- |
| id                    | INTEGER   | PK     | Payment ID                         |
| order_id              | INTEGER   | FK     | References orders.id               |
| amount                | DECIMAL   |        | Payment amount                     |
| payment_method        | TEXT      |        | Payment method                     |
| transaction_reference | TEXT      | UNIQUE | Payment reference                  |
| status                | TEXT      |        | Pending/Successful/Failed/Refunded |
| paid_at               | DATETIME  |        | Payment timestamp                  |
| created_at            | DATETIME  |        | Record creation time               |

orders 1 ───── * payments


Design Reviews

| Field       | Data Type | Key | Description            |
| ----------- | --------- | --- | ---------------------- |
| id          | INTEGER   | PK  | Review ID              |
| reviewer_id | INTEGER   | FK  | References users.id    |
| product_id  | INTEGER   | FK  | References products.id |
| order_id    | INTEGER   | FK  | References orders.id   |
| rating      | INTEGER   |     | Rating, e.g. 1–5       |
| comment     | TEXT      |     | Review text            |
| created_at  | DATETIME  |     | Review creation time   |

users 1 ───── * reviews
products 1 ───── * reviews
orders 1 ───── * reviews


                         ┌──────────────────┐
                         │      users       │
                         │──────────────────│
                         │ PK id            │
                         │ name             │
                         │ email            │
                         │ password_hash    │
                         │ role             │
                         └────────┬─────────┘
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
               ▼                  ▼                  ▼
       farmer_profiles      fpo_profiles        products
                                                   │
                                                   ▼
                                               inventory
                                                   │
                                                   │
                         ┌─────────────────────────┘
                         │
                         ▼
                     order_items
                         │
                         ▼
                       orders
                         │
                         ▼
                      payments


users
  │
  ├──────────────► bulk_requirements
  │                      │
  │                      ▼
  │                    offers
  │
  └──────────────► reviews
                         ▲
                         │
                      products


Primary keys         
         
 users.id
farmer_profiles.id
fpo_profiles.id
products.id
inventory.id
orders.id
order_items.id
bulk_requirements.id
offers.id
payments.id
reviews.id

Foreign keys

farmer_profiles.user_id → users.id

fpo_profiles.user_id → users.id

products.seller_id → users.id

inventory.product_id → products.id

orders.buyer_id → users.id

order_items.order_id → orders.id

order_items.product_id → products.id

bulk_requirements.buyer_id → users.id

offers.requirement_id → bulk_requirements.id

offers.seller_id → users.id

payments.order_id → orders.id

reviews.reviewer_id → users.id

reviews.product_id → products.id

reviews.order_id → orders.id

USERS
email must be unique
role must contain an allowed role

PRODUCTS
price >= 0
seller_id must reference an existing user

INVENTORY
quantity_available >= 0
quantity_reserved >= 0

ORDERS
buyer_id must reference an existing user
total_amount >= 0

RIVIEWS
rating must be between 1 and 5

PAYMENTS
transaction_reference should be unique
amount >= 0


## Schema Design Decisions

### 1. Users are centralized

The users table stores authentication and common account information.
Role-specific information is stored in separate profile tables.

### 2. Farmers and FPOs are producers

Both Farmers and FPOs can create product listings. Products therefore
reference users through seller_id rather than having separate farmer
and FPO product tables.

### 3. Orders and order items are separated

An order may contain multiple products, so order information and
individual product lines are stored separately.

### 4. Inventory is separated from products

Product information describes what is being sold, while inventory
tracks available and reserved quantities.

### 5. Bulk requirements and offers are separate

A bulk buyer can create a requirement and multiple producers can
respond with offers.

### 6. Payments are associated with orders

Payment records are connected to orders so that payment status can
be tracked independently from order status.

### 7. Reviews reference completed transactions

Reviews are associated with products and orders to support
transaction-based review validation.

YOU NEED TO CREATE :
farmdirect.db

Issue #7
   ↓
Design schema
   ↓
Document tables
   ↓
Define keys
   ↓
Define relationships
   ↓
Create ER diagram
   ↓
Review design
   ↓
Approve schema
   ↓
Later implementation issue
   ↓
Create SQLite database

HOW ISSUE-7 CONNECTS TO ISSUE-6
HTML/CSS
    ↓
Flask
    ↓
Business Logic
    ↓
Data Access Layer
    ↓
SQLite

ISSUE 7 NOW DEFINES WHAT EXISTS AT THE SQLite layer:
Flask Application
       ↓
Business Logic
       ↓
Data Access Layer
       ↓
SQLite
       ↓
┌──────────────────────┐
│ users                │
│ farmer_profiles      │
│ fpo_profiles         │
│ products             │
│ inventory            │
│ orders               │
│ order_items          │
│ bulk_requirements    │
│ offers               │
│ payments             │
│ reviews              │
└──────────────────────┘