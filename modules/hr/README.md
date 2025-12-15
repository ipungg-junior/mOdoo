# HR Management Module

## Overview
Human Resources management module for employee and position tracking in the mOdoo ERP system.

## Features
- Employee management linked to Django users
- Position/job title management
- Employee creation, listing, editing, and deletion
- Hire date tracking
- User synchronization

## Models
- `MasterPosition`: Job positions
- `Employee`: Employee details linked to User

## Dependencies
- Django auth (User model)

## Entry Points
- `modules/hr/apps.py`: Permission setup
- `modules/hr/urls.py`: URL routing
- `modules/hr/views.py`: Page and API views

## Public Interfaces
- API Endpoints: JSON-based endpoints with pagination
- Page Views:
  - `/hr/`: HR dashboard
  - `/hr/create/`: Employee creation
  - `/hr/list/`: Employee listing
  - `/hr/position/`: Position management

## Version
v0.1.0 - Employee and position management