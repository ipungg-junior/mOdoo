# mOdoo - Main Project

## Overview
Main Django project configuration for the mOdoo ERP system. Handles settings, URL routing, and dynamic module discovery from the `modules/` directory.

## Features
- Dynamic module loading by scanning `modules/` directory
- Centralized settings for database, authentication, and static files
- ASGI/WSGI configuration for deployment
- CSRF trusted origins for production

## Dependencies
- Django 4.2+
- SQLite (default) or PostgreSQL/MySQL

## Entry Points
- `manage.py`: Django management commands
- `mOdoo/settings.py`: Main configuration
- `mOdoo/urls.py`: Root URL configuration
- `mOdoo/wsgi.py`: WSGI entry point
- `mOdoo/asgi.py`: ASGI entry point

## Version
v0.1.0 - Initial project setup with dynamic module loading