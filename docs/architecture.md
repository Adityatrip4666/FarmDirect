# FarmDirect — System Architecture

## 1. Introduction

## 2. Architecture Overview

## 3. Technology Stack

## 4. Frontend Components

## 5. Flask Backend Components

## 6. Business Logic Layer

## 7. Database Layer

## 8. Data Flow

## 9. Authentication and Authorization Flow

## 10. Product Management Flow

## 11. Order Flow

## 12. Architecture Diagram

## 13. Project Structure

## 14. Architecture Considerations

## 1. Introduction

This document defines the high-level architecture of the FarmDirect
platform.

FarmDirect is a web-based agricultural marketplace connecting Farmers
and Farmer Producer Organizations (FPOs) with Consumers and Bulk
Buyers.

The first version of the platform will use:

- Python
- Flask
- HTML
- CSS
- SQLite

The architecture separates the presentation layer, application
backend, business logic, and data persistence responsibilities.

┌─────────────────────────────┐
│        FRONTEND             │
│        HTML + CSS            │
└──────────────┬──────────────┘
               │ HTTP
               ↓
┌─────────────────────────────┐
│       FLASK BACKEND         │
│       Routes / Views         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       BUSINESS LOGIC        │
│  Validation / Rules / Auth  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       DATABASE LAYER        │
│       SQLite / SQL          │
└─────────────────────────────┘

## 2. Architecture Overview

FarmDirect will use a layered web application architecture.

The major layers are:

1. Presentation Layer
2. Flask Application Layer
3. Business Logic Layer
4. Data Access / Database Layer

The presentation layer is responsible for the user interface.
The Flask application layer handles HTTP requests and responses.
The business logic layer implements application rules and validation.
The database layer manages persistent application data using SQLite.

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML | Page structure and forms |
| Frontend | CSS | Styling and responsive layout |
| Backend | Python | Application programming language |
| Web Framework | Flask | HTTP routing and web application framework |
| Business Logic | Python | Application rules and validation |
| Database | SQLite | Persistent data storage |
| Database Access | Python database layer | Communication with SQLite |
| Version Control | Git | Source-code version control |
| Repository | GitHub | Collaboration and code hosting |

## 4. Frontend Components

The FarmDirect frontend will provide role-specific interfaces for
different users.

### Public Components

- Home page
- Product browsing page
- Product search
- Product details
- Login page
- Registration page

### Farmer Components

- Farmer dashboard
- Farmer profile
- Product listing management
- Create product form
- Edit product form
- Farmer order/sales view

### FPO Components

- FPO dashboard
- FPO profile
- Product management
- Create/edit product forms
- FPO order/sales view

### Consumer Components

- Consumer dashboard
- Product browsing
- Product search
- Product details
- Shopping/order interface
- Order history

### Bulk Buyer Components

- Bulk buyer dashboard
- Buyer profile
- Requirement creation
- Requirement management
- Offer management
- Order management

### Administrator Components

- Admin dashboard
- User management
- Product moderation
- Marketplace monitoring
- Administrative controls

## 5. Flask Backend Components

The Flask backend will be responsible for handling HTTP requests,
authentication, authorization, application workflows, and
communication between the frontend and business logic.

Major backend components include:

### Authentication Routes

Responsible for:

- Registration
- Login
- Logout
- Session management

### User Routes

Responsible for:

- User profiles
- Farmer profiles
- FPO profiles
- Consumer profiles
- Bulk buyer profiles

### Product Routes

Responsible for:

- Creating products
- Viewing products
- Updating products
- Deleting products
- Product search
- Product filtering

### Order Routes

Responsible for:

- Creating orders
- Viewing orders
- Updating order status
- Retrieving order history

### Requirement Routes

Responsible for:

- Creating bulk buyer requirements
- Viewing requirements
- Updating requirements
- Managing requirement status

### Offer Routes

Responsible for:

- Creating offers
- Viewing offers
- Updating offers
- Managing offer status

### Administration Routes

Responsible for:

- User management
- Product moderation
- Administrative operations

## 6. Business Logic Layer

The business logic layer contains the rules that govern FarmDirect
operations.

Responsibilities include:

- User role validation
- Permission checking
- Product validation
- Product ownership validation
- Order validation
- Quantity validation
- Offer validation
- Bulk buyer requirement validation
- Business workflow management
- Status transitions
- Data consistency checks

Business logic should remain separate from HTML templates and database
operations wherever practical.

HTML Form
   ↓
POST /products
   ↓
Flask Route
   ↓
Authentication Check
   ↓
Authorization Check
   ↓
Business Logic
   ↓
Validate Product
   ↓
Database Layer
   ↓
SQLite
   ↓
Success
   ↓
Flask Response
   ↓
HTML Page

## 7. Database Layer

FarmDirect Version 1 will use SQLite as the primary database.

The database layer will be responsible for:

- Creating and retrieving records
- Updating records
- Deleting records
- Maintaining relationships between entities
- Enforcing database constraints
- Persisting application data

### Core Database Entities

The initial database design is expected to include entities such as:

- Users
- Farmer Profiles
- FPO Profiles
- Consumer Profiles
- Bulk Buyer Profiles
- Products
- Orders
- Bulk Buyer Requirements
- Offers

User
 │
 ├── Farmer Profile
 ├── FPO Profile
 ├── Consumer Profile
 └── Bulk Buyer Profile

 Farmer / FPO
     │
     └── Products
             │
             ├── Orders
             │
             └── Offers

   Bulk Buyer
     │
     └── Requirements
             │
             └── Offers

            ### Core Relationships

- A User has one assigned platform role.
- A Farmer can create multiple product listings.
- An FPO can create multiple product listings.
- A Consumer can create multiple orders.
- A Bulk Buyer can create multiple requirements.
- A product can be associated with multiple orders over its lifecycle.
- Offers are associated with the relevant buyer and producer workflow.

## 8. Data Flow

The general request flow is:

1. A user interacts with the HTML interface.
2. The browser sends an HTTP request to the Flask application.
3. Flask identifies the requested route.
4. Authentication and authorization checks are performed.
5. The relevant business logic is executed.
6. The business logic validates the request.
7. The database layer reads or writes data in SQLite when required.
8. The result is returned to Flask.
9. Flask renders an HTML response or returns the appropriate response.
10. The browser displays the result to the user.

### Product Search Flow

```text
User
  ↓
Search Form
  ↓
Flask Search Route
  ↓
Search Validation
  ↓
Business Logic
  ↓
Database Query
  ↓
SQLite
  ↓
Matching Products
  ↓
Flask
  ↓
HTML Template
  ↓
User


This demonstrates how the components interact.

---

# 21. Example: Consumer order flow

You can add:

```markdown
### Consumer Order Flow

```text
Consumer
   ↓
Product Page
   ↓
Place Order
   ↓
Flask Order Route
   ↓
Authentication
   ↓
Authorization
   ↓
Order Business Logic
   ↓
Validate Product Availability
   ↓
Create Order
   ↓
SQLite
   ↓
Order Created
   ↓
Flask Response
   ↓
Consumer Order Page




---

# 22. Example: Bulk Buyer requirement flow

Add:

```markdown
### Bulk Buyer Requirement Flow

```text
Bulk Buyer
    ↓
Requirement Form
    ↓
Flask Requirement Route
    ↓
Authentication / Authorization
    ↓
Requirement Validation
    ↓
Business Logic
    ↓
SQLite
    ↓
Requirement Created
    ↓
Producer can discover relevant requirement
    ↓
Offer


This connects Issue #3's bulk-buyer requirements and offers to the architecture.

---

# 23. Step 16 — Authentication and authorization flow

Since Issue #2 defined roles and Issue #3 defined authentication requirements, show how they fit into the architecture.

Add:

```markdown
## 9. Authentication and Authorization Flow

The authentication and authorization flow will operate as follows:

```text
User
  ↓
Login Form
  ↓
Flask Authentication Route
  ↓
Validate Credentials
  ↓
Retrieve User
  ↓
Create Authenticated Session
  ↓
Identify User Role
  ↓
Role-Based Authorization
  ↓
Allow / Reject Requested Operation


This distinction is very important.

---

# 24. Step 17 — Create the architecture diagram

This is the biggest acceptance criterion:

> **Architecture diagram is added to the repository.**

The easiest option is to use **Mermaid** inside your Markdown file.

Add:

```markdown
## 12. Architecture Diagram

```mermaid
flowchart TD

    U[Users]

    FE[Frontend<br/>HTML + CSS]

    FLASK[Flask Backend<br/>Routes / Controllers]

    AUTH[Authentication & Authorization]

    BL[Business Logic Layer<br/>Validation / Rules / Workflows]

    DAL[Database Access Layer]

    DB[(SQLite Database)]

    U --> FE
    FE -->|HTTP Request| FLASK
    FLASK --> AUTH
    AUTH --> BL
    FLASK --> BL
    BL --> DAL
    DAL --> DB

    DB --> DAL
    DAL --> BL
    BL --> FLASK
    FLASK -->|HTTP Response| FE
    FE --> U

  
GitHub supports Mermaid diagrams in Markdown, so this can serve as your architecture diagram directly in the repository.

Your diagram conceptually shows:

```text
Users
  ↓
HTML + CSS
  ↓
Flask
  ↓
Authentication / Authorization
  ↓
Business Logic
  ↓
Database Access
  ↓
SQLite

```mermaid
flowchart TD

    subgraph USERS[FarmDirect Users]
        F[Farmer]
        O[FPO]
        C[Consumer]
        B[Bulk Buyer]
        A[Administrator]
    end

    subgraph FRONTEND[Frontend - HTML + CSS]
        PUB[Public Pages]
        AUTHUI[Login / Registration]
        PRODUI[Product Interface]
        ORDERUI[Order Interface]
        REQUI[Bulk Requirements]
        OFFERUI[Offer Interface]
        ADMINUI[Admin Interface]
    end

    subgraph BACKEND[Flask Backend]
        ROUTES[Flask Routes]
        AUTH[Authentication & Authorization]
        SERVICES[Business Logic]
        VALID[Validation]
    end

    subgraph DATA[Database Layer]
        DAL[Data Access]
        SQLITE[(SQLite)]
    end

    F --> FRONTEND
    O --> FRONTEND
    C --> FRONTEND
    B --> FRONTEND
    A --> FRONTEND

    FRONTEND --> ROUTES
    ROUTES --> AUTH
    AUTH --> VALID
    VALID --> SERVICES
    SERVICES --> DAL
    DAL --> SQLITE

    SQLITE --> DAL
    DAL --> SERVICES
    SERVICES --> ROUTES
    ROUTES --> FRONTEND

    
This is much closer to what your issue asks for.

---

# 26. Step 18 — Document the project structure

Because you're using Flask, I'd recommend documenting a proposed project structure.

Add:

```markdown
## 13. Project Structure

The initial application structure is expected to follow a structure
similar to:

```text
FarmDirect/
│
├── app/
│   ├── __init__.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── requirements.py
│   │   ├── offers.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── requirement_service.py
│   │   └── offer_service.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── requirement.py
│   │   └── offer.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── farmer/
│   │   ├── fpo/
│   │   ├── consumer/
│   │   ├── bulk_buyer/
│   │   └── admin/
│   │
│   └── static/
│       └── css/
│
├── docs/
│
├── tests/
│
├── instance/
│   └── farmdirect.db
│
├── requirements.txt
└── run.py


### Important

This is a **proposed architecture**, not something you need to create now.

Don't create all these folders just because they're in the architecture document.

Your current issue is about **designing the architecture**.

Actual implementation can come in later issues.

---

# 27. Step 19 — Explain why the layers are separated

Add:

```markdown
## 14. Architecture Considerations

The architecture separates responsibilities to make the application
easier to understand, test, maintain, and extend.

### Frontend

Responsible for presentation and user interaction.

### Flask Backend

Responsible for handling HTTP requests and responses.

### Business Logic

Responsible for application rules, validation, authorization-related
decisions, and workflows.

### Database Layer

Responsible for persistence and communication with SQLite.

This separation reduces unnecessary coupling between the user
interface, business rules, and database implementation.

Flask Route
     ↓
Service / Business Logic
     ↓
Data Access
     ↓
SQLite