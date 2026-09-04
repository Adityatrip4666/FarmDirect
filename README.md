# FarmDirect — Direct Farmer-to-Buyer Marketplace

## 1. Project Overview

**FarmDirect** is a web-based digital marketplace designed to connect farmers and Farmer Producer Organizations (FPOs) directly with consumers and bulk buyers.

The platform aims to reduce unnecessary intermediaries in the agricultural supply chain, helping farmers receive better prices while providing consumers and bulk buyers with easier access to agricultural products.

The project is developed using **Python, Flask, HTML, CSS, and SQLite**.

---

## 2. Problem Statement

Multiple intermediaries are involved in the traditional agricultural supply chain. This can reduce the earnings received by farmers while increasing the final price paid by consumers.

FarmDirect addresses this problem by providing a digital platform where farmers/FPOs can list their products and connect directly with consumers and bulk buyers.

---

## 3. Project Objectives

The main objectives of FarmDirect are:

* Connect farmers/FPOs directly with consumers and bulk buyers.
* Allow farmers to list and manage their agricultural products.
* Provide consumers with an easy way to discover and purchase produce.
* Enable bulk buyers to find products in larger quantities.
* Reduce unnecessary intermediaries in the supply chain.
* Provide basic order and delivery management.
* Improve transparency between farmers and buyers.

---

## 4. Target Users

### Farmers / FPOs

Farmers and FPOs can use the platform to:

* Create and manage their profiles.
* List agricultural products.
* Specify quantity, price, location, and availability.
* Manage available stock.
* View incoming orders.
* Accept or reject orders.
* Update order status.

### Consumers

Consumers can:

* Create an account.
* Browse available agricultural products.
* Search and filter products.
* View product and farmer information.
* Add products to a cart.
* Place orders.
* View order history.
* Track order status.

### Bulk Buyers

Bulk buyers such as retailers, restaurants, hotels, and food businesses can:

* Search for agricultural products.
* Find products available in larger quantities.
* View farmer/FPO information.
* Place bulk orders.
* Track their orders.

### Administrator

The administrator manages the overall platform and can:

* Manage users.
* Manage product listings.
* Monitor orders.
* Manage delivery information.
* View basic marketplace statistics.

---

## 5. Core Features

### User Authentication

* User registration and login.
* Role-based access.
* Separate dashboards for different user types.
* Secure password handling.

### Product Management

Farmers/FPOs can create product listings containing:

* Product name
* Category
* Quantity
* Price
* Location
* Harvest date
* Availability

Farmers can also edit or remove their listings.

### Marketplace

The marketplace allows buyers to:

* Browse available products.
* Search for specific products.
* Filter products by price and location.
* View product details.
* View information about the farmer/FPO.

### Cart and Orders

Consumers can:

1. Select a product.
2. Add it to the cart.
3. Specify quantity.
4. Place an order.
5. View the order status.

Farmers can view and manage incoming orders.

### Bulk Orders

Bulk buyers can search for products based on their required quantity and place larger orders directly with farmers/FPOs.

### Delivery Management

The platform provides basic delivery management by storing:

* Pickup location
* Delivery location
* Estimated delivery information
* Delivery status

Order statuses can include:

```text
Placed
  ↓
Accepted
  ↓
Preparing
  ↓
Picked Up
  ↓
Out for Delivery
  ↓
Delivered
```

### Admin Dashboard

The administrator can monitor:

* Total users
* Registered farmers/FPOs
* Available products
* Total orders
* Pending orders
* Completed orders

---

## 6. System Architecture

The application follows a simple web application architecture:

```text
User
  │
  ▼
HTML + CSS Interface
  │
  ▼
Flask Application
  │
  ├── Authentication
  ├── Marketplace
  ├── Product Management
  ├── Order Management
  └── Delivery Management
  │
  ▼
SQLAlchemy
  │
  ▼
SQLite Database
```

---

## 7. Technology Stack

| Component       | Technology   |
| --------------- | ------------ |
| Backend         | Python       |
| Web Framework   | Flask        |
| Frontend        | HTML5        |
| Styling         | CSS3         |
| Template Engine | Jinja2       |
| Database        | SQLite       |
| Database ORM    | SQLAlchemy   |
| Version Control | Git / GitHub |

---

## 8. Database Design

The initial database consists of the following main entities:

### User

Stores information about registered users.

```text
id
name
email
password
phone
role
location
```

### Product

Stores agricultural product listings.

```text
id
farmer_id
name
category
quantity
price
location
harvest_date
availability
```

### Order

Stores order information.

```text
id
buyer_id
farmer_id
product_id
quantity
total_price
status
order_date
```

### Delivery

Stores delivery-related information.

```text
id
order_id
pickup_location
delivery_location
estimated_time
status
```

---

## 9. Main Application Pages

The application will contain pages such as:

```text
Home
Login
Register

Farmer Dashboard
 ├── Profile
 ├── Add Product
 ├── My Products
 └── Orders

Marketplace
 ├── Product Search
 ├── Product Details
 └── Cart

Consumer
 ├── Checkout
 ├── My Orders
 └── Order Tracking

Bulk Buyer
 ├── Product Search
 ├── Bulk Orders
 └── Order Tracking

Admin
 ├── Dashboard
 ├── Users
 ├── Products
 ├── Orders
 └── Deliveries
```

---

## 10. Project Structure

The planned project structure is:

```text
FarmDirect/
│
├── app.py
├── models.py
├── database.py
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── farmer_dashboard.html
│   ├── add_product.html
│   ├── marketplace.html
│   ├── product_details.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   └── admin_dashboard.html
│
├── static/
│   └── css/
│       └── style.css
│
├── instance/
│   └── farmdirect.db
│
└── README.md
```

---

## 11. Basic User Flow

### Farmer

```text
Register
   ↓
Create Profile
   ↓
Add Agricultural Product
   ↓
Product Listed on Marketplace
   ↓
Receive Order
   ↓
Accept Order
   ↓
Prepare Product
   ↓
Update Order Status
```

### Consumer

```text
Register
   ↓
Browse Marketplace
   ↓
Search Product
   ↓
View Product Details
   ↓
Add to Cart
   ↓
Place Order
   ↓
Track Order
   ↓
Receive Product
```

### Bulk Buyer

```text
Register
   ↓
Search Product
   ↓
Check Available Quantity
   ↓
Select Farmer/FPO
   ↓
Place Bulk Order
   ↓
Track Order
```

---

## 12. MVP Scope

The initial version of FarmDirect will focus on the following features:

* User registration and authentication
* Farmer/FPO product listing
* Product marketplace
* Product search and filtering
* Shopping cart
* Order placement
* Farmer order management
* Bulk ordering
* Basic delivery tracking
* Admin dashboard

The MVP will focus on demonstrating the **core farmer-to-buyer marketplace workflow** rather than implementing a large number of advanced features.

---

## 13. Future Enhancements

Possible future improvements include:

* Online payment gateway integration
* Real-time delivery tracking
* Mobile application
* Multilingual support
* Voice-based interaction for farmers
* Product quality verification
* Warehouse and cold-storage integration
* Government scheme integration
* Advanced analytics and reporting

---

## 14. Expected Impact

FarmDirect aims to create a more direct and transparent agricultural marketplace by reducing unnecessary intermediaries.

The expected benefits are:

**For Farmers**

* Better access to buyers
* Improved price transparency
* Wider customer reach

**For Consumers**

* Direct access to agricultural products
* Better price visibility
* Information about the source of produce

**For Bulk Buyers**

* Easier supplier discovery
* Access to larger quantities
* Direct communication with producers

---

## 15. Success Criteria

The MVP will be considered successful if:

* Farmers can successfully list agricultural products.
* Consumers can discover and order products.
* Bulk buyers can place larger orders.
* Farmers can manage incoming orders.
* Buyers can track order status.
* Administrators can monitor platform activity.
* The complete farmer-to-buyer transaction can be demonstrated successfully.

---

## 16. Development Approach

The project follows the initial stages of the **Software Development Life Cycle (SDLC)**:

```text
Planning
   ↓
Requirements Analysis
   ↓
System Design
   ↓
Development
   ↓
Testing
   ↓
Deployment
   ↓
Maintenance
```

This README currently focuses on the first three stages:

1. **Planning** — defining the problem, objectives, users, and MVP scope.
2. **Requirements Analysis** — identifying functional and non-functional requirements.
3. **System Design** — defining the application architecture, database, modules, and user flows.

---

## 17. Conclusion

FarmDirect is intended to provide a simple and accessible digital marketplace that brings farmers/FPOs closer to their end buyers.

By combining a straightforward web interface with a Python Flask backend and a relational database, the project provides a practical foundation for improving direct agricultural commerce.

The initial focus is on building a functional MVP that demonstrates the complete flow from **product listing → buyer discovery → order placement → order management → delivery tracking**.
