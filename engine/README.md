# Engine - Core Module

## Overview
Core application engine for the mOdoo ERP system. Provides module management, user permissions, base templates, and shared utilities.

## Features
- Dynamic module installation/uninstallation
- Role-based access control with group permissions
- Base HTML templates with Tailwind styling
- Shared utilities
- Automatic URL registration for installed modules

## Models
- `Module`: Tracks installed modules
- `MasterDatabase`: Shared database references

## Dependencies
- Django auth, contenttypes, sessions
- Bootstrap/Tailwind CSS for UI

## Entry Points
- `engine/apps.py`: Permission setup on app ready
- `engine/urls.py`: Core URL patterns
- `engine/views.py`: Module management views
- `engine/templates/base_template.html`: Base template

## Public Interfaces
- Module management API
- Base templates for inheritance
- `format_rupiah()` utility function

## Version
v0.1.0 - Core module management and permissions