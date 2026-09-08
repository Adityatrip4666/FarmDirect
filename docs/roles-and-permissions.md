# FarmDirect — Roles and Permissions

## Overview

FarmDirect supports multiple user roles with different responsibilities
and access permissions.

The initial system supports the following roles:

- Farmer
- FPO
- Consumer
- Bulk Buyer
- Administrator

Each role has specific permissions based on its responsibilities.
Access to functionality is restricted according to the user's role.

## 1. Farmer

### Description

A Farmer is an individual agricultural producer who uses FarmDirect
to create a producer profile, list agricultural products, and make
those products available to consumers and bulk buyers.

### Responsibilities

- Maintain accurate producer information.
- Create and maintain product listings.
- Provide accurate product details.
- Manage the availability of their own products.
- Respond to relevant buyer interactions.

### Permissions

A Farmer can:

- Register an account.
- Log in and log out.
- Manage their own profile.
- Create product listings.
- Edit their own product listings.
- Delete their own product listings.
- View marketplace products.
- Search and filter products.
- View buyer-related information that the system makes available to them.
- Manage their own orders or sales-related information as supported
  by the system.

### Restrictions

A Farmer cannot:

- Modify another farmer's profile.
- Modify another farmer's products.
- Manage FPO accounts.
- Manage consumer accounts.
- Manage administrator accounts.
- Modify system-wide settings.
- Manage other users' permissions.

## 2. FPO

### Description

An FPO (Farmer Producer Organization) represents a group of farmers
and uses FarmDirect to manage its organization profile and agricultural
product listings.

### Responsibilities

- Maintain accurate FPO information.
- Manage FPO product listings.
- Represent products supplied by associated farmers.
- Provide accurate product and availability information.
- Manage relevant buyer interactions.

### Permissions

An FPO can:

- Register an account.
- Log in and log out.
- Manage its FPO profile.
- Create product listings.
- Edit its own product listings.
- Delete its own product listings.
- View marketplace products.
- Search and filter products.
- View relevant buyer information.
- Manage its own marketplace transactions as supported by the system.

### Restrictions

An FPO cannot:

- Modify another FPO's profile.
- Modify another FPO's products.
- Modify administrator accounts.
- Change system-wide settings.
- Manage user roles and permissions.
- Access another organization's private information without
  authorization.

  ## 3. Consumer

### Description

A Consumer is an individual buyer who uses FarmDirect to discover
and purchase agricultural products from farmers and FPOs.

### Responsibilities

- Provide accurate account information.
- Review product information before purchasing.
- Provide accurate order information.
- Manage their own account and orders.

### Permissions

A Consumer can:

- Register an account.
- Log in and log out.
- Manage their own profile.
- Browse agricultural products.
- Search for products.
- Filter products.
- View product details.
- View farmer and FPO information made publicly available.
- Place orders, where supported.
- View their own orders.
- Manage their own order-related information.

### Restrictions

A Consumer cannot:

- Create farmer product listings.
- Edit farmer product listings.
- Edit FPO product listings.
- Modify another consumer's account.
- Access administrator functionality.
- Manage user roles.
- Modify system-wide settings.

## 4. Bulk Buyer

### Description

A Bulk Buyer is a business, organization, retailer, restaurant,
institution, wholesaler, or other buyer seeking agricultural products
in larger quantities.

### Responsibilities

- Provide accurate buyer information.
- Identify required products and quantities.
- Submit purchase or bulk-order requests.
- Manage their own orders and buyer information.

### Permissions

A Bulk Buyer can:

- Register an account.
- Log in and log out.
- Manage their own profile.
- Browse agricultural products.
- Search for products.
- Filter products.
- View product details.
- View farmer and FPO information made available by the platform.
- Submit bulk purchase or order requests, where supported.
- View their own orders.
- Manage their own order-related information.

### Restrictions

A Bulk Buyer cannot:

- Create farmer product listings.
- Edit farmer product listings.
- Edit FPO product listings.
- Modify another buyer's account.
- Manage administrator accounts.
- Change system-wide settings.
- Manage user roles and permissions.

## 5. Administrator

### Description

The Administrator manages the FarmDirect platform and has elevated
permissions required to maintain users, marketplace data, and system
operations.

### Responsibilities

- Manage platform users.
- Maintain platform integrity.
- Manage inappropriate or invalid content.
- Monitor marketplace activity.
- Manage system-level configuration where applicable.
- Support users when administrative intervention is required.

### Permissions

An Administrator can:

- Log in to the administrator interface.
- View user accounts.
- Manage user accounts.
- Manage farmer accounts.
- Manage FPO accounts.
- Manage consumer accounts.
- Manage bulk buyer accounts.
- Review product listings.
- Remove inappropriate or invalid listings.
- Manage user roles where authorized.
- Access administrative information.
- Manage system-level settings where implemented.

### Restrictions

An Administrator should not:

- Modify data without an administrative reason.
- Impersonate users without authorization.
- Access sensitive information beyond their administrative requirements.
- Perform actions outside their assigned administrative privileges.

## Role-Permission Matrix

                  | Permission | Farmer | FPO | Consumer | Bulk Buyer | Administrator |
                             |---|---|---|---|---|---|
| Register account           | Yes | Yes | Yes | Yes | No* |
| Login                      | Yes | Yes | Yes | Yes | Yes |
| Manage own profile         | Yes | Yes | Yes | Yes | Yes |
| Browse products            | Yes | Yes | Yes | Yes | Yes |
| Search products            | Yes | Yes | Yes | Yes | Yes |
| Filter products            | Yes | Yes | Yes | Yes | Yes |
| Create product listing     | Yes | Yes | No | No | Yes |
| Edit own product listing   | Yes | Yes | No | No | Yes |
| Delete own product listing | Yes | Yes | No | No | Yes |
| Place consumer order       | No | No | Yes | No | No |
| Submit bulk order          | No | No | No | Yes | No |
| View own orders            | Yes* | Yes* | Yes | Yes | Yes* |
| Manage users               | No | No | No | No | Yes |
| Manage roles               | No | No | No | No | Yes |
| Moderate listings          | No | No | No | No | Yes |
| Manage system settings     | No | No | No | No | Yes |


## Unauthorized Actions by Role

### Farmer

A Farmer must not:

- Edit another farmer's products.
- Delete another farmer's products.
- Access administrator functionality.
- Manage other users.
- Change user roles.
- Modify system configuration.

### FPO

An FPO must not:

- Modify another FPO's data.
- Modify unrelated farmers' private information.
- Manage consumers or bulk buyers.
- Change user roles.
- Access administrator functionality.
- Modify system configuration.

### Consumer

A Consumer must not:

- Create or modify producer product listings.
- Access farmer or FPO management functions.
- Modify another user's account.
- Manage user roles.
- Access administrator functions.
- Modify system configuration.

### Bulk Buyer

A Bulk Buyer must not:

- Create or modify farmer product listings.
- Create or modify FPO product listings.
- Modify another buyer's account.
- Manage user roles.
- Access administrator functions.
- Modify system configuration.

### Administrator

An Administrator must not:

- Access or modify information without a legitimate administrative
  purpose.
- Perform actions outside their assigned administrative permissions.
- Circumvent platform security controls.
- Modify data arbitrarily.

## Access Control Principles

FarmDirect will follow these principles:

1. Users can access functionality according to their assigned role.

2. Users should only be able to modify resources they own or are
   explicitly authorized to manage.

3. Administrative functionality is restricted to Administrators.

4. Unauthorized actions must be rejected by the system.

5. Role permissions should be enforced on the backend and not only
   through the user interface.

6. Users should not be able to gain additional permissions by
   manipulating client-side requests or interface elements.
