# FarmDirect — Direct Farmer-to-Buyer Agricultural Marketplace

FarmDirect is a web-based agricultural marketplace that connects farmers and
Farmer Producer Organizations (FPOs) directly with consumers and bulk buyers.

The system allows sellers to list agricultural products, buyers to search and
purchase products, bulk buyers to post requirements and receive offers, and
administrators to manage the platform.

## 1. Project Overview

FarmDirect aims to provide a simple digital marketplace for direct
farmer-to-buyer transactions.

The application is developed using:

- Python
- Flask
- HTML5
- CSS3
- Jinja2
- SQLite
- Git/GitHub
- Pytest

## 2. Problem Statement

Traditional agricultural supply chains can involve multiple intermediaries
between producers and buyers.

FarmDirect provides a digital platform where farmers/FPOs can list products
and connect directly with consumers and bulk buyers.

## 3. Objectives

The main objectives are:

- Connect farmers/FPOs with consumers and bulk buyers.
- Allow farmers/FPOs to manage agricultural product listings.
- Provide product search and filtering.
- Provide shopping cart and order functionality.
- Support bulk buyer requirements and seller offers.
- Provide reviews and ratings.
- Provide user notifications.
- Provide role-based access control.
- Provide an administrator dashboard.
- Provide an AI-assisted agricultural price suggestion feature.
- Maintain secure authentication and database operations.

## 4. User Roles

### Farmer / FPO

Farmers and FPOs can:

- Register and log in.
- Manage their profiles.
- Add agricultural products.
- Edit their own products.
- Delete their own products.
- View their products.
- Receive notifications.
- Manage incoming orders.
- Respond to bulk buyer requirements.
- View offer status notifications.
- Request AI-assisted price suggestions.

### Consumer

Consumers can:

- Register and log in.
- Browse the marketplace.
- Search and filter products.
- Add products to a cart.
- Update cart quantities.
- Place orders.
- View order history.
- View order details.
- Review purchased products.
- Rate products from 1 to 5.
- View product ratings and reviews.
- View notifications.

### Bulk Buyer

Bulk buyers can:

- Register and log in.
- Browse the marketplace.
- Search for products.
- Create bulk requirements.
- Specify required quantity and maximum price.
- Receive offers from farmers/FPOs.
- Accept or reject offers.
- View relevant notifications.

### Administrator

Administrators can:

- Access the administrator dashboard.
- View marketplace statistics.
- Manage users.
- Activate/deactivate user accounts.
- Manage product listings.
- Monitor platform activity.

## 5. Main Features

### Authentication

- User registration
- User login
- User logout
- Password hashing
- Session management
- Inactive-account protection

Administrators are not available through normal public registration.

### Role-Based Access Control

The application restricts functionality according to user role.

Examples:

- Consumers cannot manage farmer products.
- Farmers/FPOs cannot access consumer cart functionality.
- Non-admin users cannot access administrator functions.
- Sellers can only modify their own products.
- Users can only access their own notifications.

### Product Management

Farmers/FPOs can create product listings containing:

- Product name
- Category
- Quantity
- Price
- Location
- Quality details
- Availability

Sellers can edit and delete their own listings.

### Marketplace

Consumers and bulk buyers can:

- Browse available products.
- Search by product name.
- Filter by category.
- Filter by maximum price.
- Filter by location.
- View product information.
- View product reviews and ratings.

### Shopping Cart

Consumers can:

- Add products to the cart.
- Update quantities.
- Remove products.
- Clear the cart.
- Place orders.

### Consumer Orders

Consumers can:

- Place orders.
- View order history.
- View order details.
- View order status.

### Bulk Buyer Requirements

Bulk buyers can create requirements specifying:

- Product
- Required quantity
- Maximum price
- Delivery/location information
- Requirement details

Farmers/FPOs can respond with offers.

### Bulk Buyer Offers

Farmers/FPOs can submit offers against suitable bulk requirements.

Bulk buyers can accept or reject offers.

Offer status changes generate relevant notifications.

### Reviews and Ratings

Consumers can review products they have purchased.

Features include:

- Rating from 1 to 5.
- Written review.
- Purchase verification.
- Duplicate-review prevention.
- Product review listing.
- Average product rating.

### Notifications

The application provides notifications for relevant marketplace events.

Examples include:

- New order received by a seller.
- New bulk requirement posted.
- New offer received by a bulk buyer.
- Offer accepted or rejected.

Users can view their notifications and mark unread notifications as read.

### AI-Assisted Price Suggestion

Farmers/FPOs can request an advisory price suggestion while adding a product.

The suggestion uses product information such as:

- Product name
- Category
- Quantity
- Location
- Quality details

The suggested price is advisory only.

The seller can:

- Use the suggestion as a reference.
- Modify the final price.
- Ignore the suggestion.

The system never automatically overwrites the seller's final product price.

The current implementation is a local deterministic price-suggestion engine intended
for the college-project prototype and does not require an external AI API.

### Administrator Dashboard

The administrator dashboard provides basic platform statistics, including:

- Total users
- Farmers/FPOs
- Consumers
- Bulk buyers
- Products
- Orders
- Open bulk requirements
- Pending offers

## 6. System Architecture

```text
User
  |
  v
HTML / CSS / Jinja2
  |
  v
Flask Application
  |
  +-- Authentication
  +-- Role-Based Access Control
  +-- Product Management
  +-- Marketplace
  +-- Shopping Cart
  +-- Order Management
  +-- Bulk Requirements
  +-- Offers
  +-- Reviews & Ratings
  +-- Notifications
  +-- AI Price Suggestion
  +-- Administration
  |
  v
SQLite Database