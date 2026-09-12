# FarmDirect User Workflows

## Overview

This document defines the major workflows for the FarmDirect platform.

The workflows cover authentication and the main activities of
Farmers/FPOs, Consumers, Bulk Buyers, and Administrators.

Normal operations and important alternative/error scenarios are
also documented.

Normal authentication flow

User
  ↓
Open Login Page
  ↓
Enter Email and Password
  ↓
Submit Login Form
  ↓
Validate Input
  ↓
Check User Credentials
  ↓
Credentials Valid?
  ├── No → Show Login Error
  │
  └── Yes
        ↓
     Create Session
        ↓
     Identify User Role
        ↓
     Redirect to Role Dashboard

     ## 1. Authentication Workflow

### Normal Flow

1. User opens the FarmDirect login page.
2. User enters email and password.
3. System validates the required fields.
4. System checks the user account.
5. System verifies the password.
6. If credentials are valid, a session is created.
7. The user's role is identified.
8. User is redirected to the appropriate dashboard.

Invalid  credentials

User
 ↓
Login
 ↓
Invalid email/password
 ↓
Show error
 ↓
User tries again


Empty fields

Login form
 ↓
Required field missing
 ↓
Validation error
 ↓
Stay on login page


Unregistered user

Login
 ↓
Account does not exist
 ↓
Show account-not-found/login error


Logout

Logged-in User
 ↓
Logout
 ↓
Session cleared
 ↓
Redirect to login/home page

Unauthorized access

Logged-out user
 ↓
Attempts protected page
 ↓
System checks session
 ↓
No valid session
 ↓
Access denied
 ↓
Redirect to login


Farmer/FPO Workflow

Farmers and FPOs are producers, so their workflow should focus on:

Profile
Products
Inventory
Orders/offers
Managing their own resources

Normal workflow

Farmer/FPO
    ↓
Login
    ↓
Dashboard
    ↓
Manage Profile
    ↓
Create/Edit Product
    ↓
Set Price & Quantity
    ↓
Product Saved
    ↓
Manage Inventory
    ↓
View Orders / Offers
    ↓
Update Status


Farmer/FPO Error Scenarios

Include things like:

Invalid product information

Add Product
 ↓
Missing/invalid information
 ↓
Validation error
 ↓
Correct information
 ↓
Submit again


Insufficient inventory

Order received
 ↓
Check inventory
 ↓
Insufficient quantity
 ↓
Order cannot be fulfilled
 ↓
Show appropriate status/message


Unauthorized product modification

Farmer A
 ↓
Attempts to edit Farmer B's product
 ↓
Ownership check
 ↓
Access denied

This directly connects to Issue #2 and Issue #11.


Consumer Workflow

The Consumer workflow should represent the normal buying process.

Normal flow:

Consumer
   ↓
Login
   ↓
Consumer Dashboard
   ↓
Browse Products
   ↓
Search / Filter
   ↓
View Product Details
   ↓
Select Quantity
   ↓
Place Order
   ↓
Validate Availability
   ↓
Create Order
   ↓
Payment
   ↓
Order Confirmation
   ↓
Track/View Order
   ↓
Complete Order
   ↓
Submit Review

## 3. Consumer Workflow

### Normal Flow

1. Consumer logs into FarmDirect.
2. Consumer opens the product marketplace.
3. Consumer searches or filters products.
4. Consumer views product details and producer information.
5. Consumer selects the required quantity.
6. System validates product availability.
7. Consumer places the order.
8. System creates the order.
9. Payment is processed according to the available payment workflow.
10. Consumer receives order confirmation.
11. Consumer can view the order status.
12. After completing the purchase, the consumer can submit a review.


Consumer Error Scenarios

Product unavailable:
Consumer selects product
 ↓
System checks inventory
 ↓
Insufficient stock
 ↓
Order rejected/not completed
 ↓
User receives message
Invalid quantity
Quantity entered
 ↓
Quantity invalid
 ↓
Validation error
 ↓
User enters valid quantity


Failed payment:
Place Order
 ↓
Payment
 ↓
Payment fails
 ↓
Order/payment status updated
 ↓
User informed


Unauthorized order access:
Consumer A
 ↓
Attempts to view Consumer B's order
 ↓
Authorization check
 ↓
Access denied


Bulk Buyer Workflow

This is one of FarmDirect's important differentiating workflows.

The bulk buyer doesn't necessarily start by choosing a product listing.

Instead, they can post a requirement.

Normal workflow:
Bulk Buyer
   ↓
Login
   ↓
Dashboard
   ↓
Create Bulk Requirement
   ↓
Enter Product & Quantity
   ↓
Set Target Price / Delivery Details
   ↓
Submit Requirement
   ↓
Requirement Published
   ↓
Farmers/FPOs View Requirement
   ↓
Producers Submit Offers
   ↓
Bulk Buyer Reviews Offers
   ↓
Compare Offers
   ↓
Accept Offer
   ↓
Transaction
   ↓
Order/Payment Processing


Bulk Buyer Error Scenarios

Invalid requirement:
Create Requirement
 ↓
Missing quantity/product/date
 ↓
Validation error
 ↓
Correct details

No offers:
Requirement published
 ↓
No producers respond
 ↓
Requirement remains open
 ↓
Buyer can wait/update/close requirement

Offer rejected:
Offer received
 ↓
Buyer reviews
 ↓
Offer rejected
 ↓
Requirement remains open

Unauthorized requirement modification:
Bulk Buyer A
 ↓
Attempts to modify Buyer B's requirement
 ↓
Ownership check
 ↓
Access denied


Administrator Workflow

Administrator has system-level responsibilities.

Normal workflow:
Administrator
      ↓
Login
      ↓
Admin Dashboard
      ↓
Manage Users
      ↓
Manage Products
      ↓
Monitor Marketplace
      ↓
Review Suspicious/Inappropriate Content
      ↓
Take Authorized Action
      ↓
Update System Data


 Administrator Error Scenarios

Non-admin tries admin page:
Consumer
 ↓
/admin
 ↓
Role check
 ↓
Not Administrator
 ↓
Access denied

Invalid administrative action:
Admin
 ↓
Attempts invalid action
 ↓
System validation
 ↓
Action rejected
 ↓
Error message

User/product doesn't exist:
Admin
 ↓
Search resource
 ↓
Resource not found
 ↓
Show appropriate message


Workflow summary

| Role          | Main Activities                                                  |
| ------------- | ---------------------------------------------------------------- |
| Farmer/FPO    | Manage profile, products, inventory, orders and offers           |
| Consumer      | Search products, place orders, make payments and review products |
| Bulk Buyer    | Create requirements, receive offers and manage bulk transactions |
| Administrator | Manage users, products and marketplace activities                |

Error-Flow summary

| Scenario                           | Expected System Behavior                         |
| ---------------------------------- | ------------------------------------------------ |
| Invalid login                      | Reject login and show error                      |
| Empty required field               | Show validation message                          |
| Duplicate registration             | Prevent account creation                         |
| Unauthorized page                  | Deny access                                      |
| Unauthorized resource modification | Deny action                                      |
| Insufficient inventory             | Prevent/flag order                               |
| Invalid order quantity             | Reject input                                     |
| Failed payment                     | Update payment/order status                      |
| No bulk offers                     | Keep requirement open or allow buyer to close it |
| Invalid admin action               | Reject action                                    |
