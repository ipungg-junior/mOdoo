# mOdoo - Modular Django ERP System

mOdoo is a comprehensive Django-based Enterprise Resource Planning (ERP) system featuring dynamic module loading, role-based access control, and modern web interfaces. Built with a modular architecture that allows seamless extension and customization.

## Features

### Core Engine
- **Dynamic Module Management**: Install, uninstall, and upgrade modules at runtime without server restart
- **Permission-Based Access Control**: Advanced role-based permissions with group management
- **Dynamic URL Routing**: Automatic URL registration for installed modules
- **Bootstrap UI**: Clean, responsive interface for module management

### Available Modules

#### **Product Management Module**
- **Models**: Category, Product with foreign key relationships
- **Features**:
  - Complete CRUD operations for products and categories
  - Product categorization system
  - Active/inactive status management
  - Price and inventory tracking
- **UI**: Dashboard with product table, create/edit forms, category management
- **API**: RESTful endpoints for all operations

#### **HR Management Module**
- **Models**: MasterPosition, Employee (linked to Django User)
- **Features**:
  - Employee management with user integration
  - Position/job title management
  - Employee creation, listing, editing, and deletion
  - Sync employees from existing users
  - Hire date tracking
- **UI**: Multiple pages (index, list, create, position management)
- **API**: JSON-based endpoints with pagination support

#### **Extensible Architecture**
- Easy to add new business modules
- Service layer pattern for business logic
- Template inheritance system
- Consistent API patterns across modules

## Architecture

### Project Structure
```
mOdoo/
├── engine/                          # Core application engine
│   ├── models.py                   # Module management models
│   ├── views.py                    # Module management views
│   ├── urls.py                     # Core URL patterns
│   ├── apps.py                     # Dynamic permission creation
│   └── templates/                  # Core templates
│       ├── base_template.html      # Base template with navigation
│       ├── home.html              # Home page
│       ├── login.html             # Login page
│       └── module_list.html       # Module management interface
├── modules/                         # Pluggable business modules
│   ├── <module_name>/                         # HR Management Module
│   │   ├── models.py              # Employee, MasterPosition models
│   │   ├── views.py               # Page and API views
│   │   ├── services.py            # Business logic layer
│   │   ├── urls.py                # URL routing
│   │   ├── apps.py                # Permission setup
│   │   └── templates/             # HR-specific templates
│   │       ├── module_index.html      # HR dashboard
│   │       └── base_module_sidenav.html # HR navigation
│   ├── <other_module>/               # Placeholder module
│   └── updater.py                  # Module management utilities
├── mOdoo/                          # Django project settings
│   ├── settings.py                # Main configuration
│   ├── urls.py                    # Root URL configuration
│   ├── wsgi.py                    # WSGI configuration
│   └── asgi.py                    # ASGI configuration
├── README.md                      # This documentation
├── manage.py                      # Django management script
└── .gitignore                     # Git ignore rules
```

### Technical Architecture

#### **Service Layer Pattern**
- Business logic separated into service classes
- Clean separation between views and logic
- Easy to test and maintain

#### **API-Driven Frontend**
- JSON-based communication between frontend and backend
- Consistent error handling and response formats
- Real-time updates without page reloads

#### **Permission System**
- Module-level access control (`engine.access_<module_name>`)
- Model-specific permissions (view, add, change, delete)
- Group-based user management
- Dynamic permission creation on module installation

#### **Template System**
- Base template inheritance
- Reusable components (sidebars, navigation)
- Responsive Bootstrap/Tailwind CSS styling
- Consistent UI patterns across modules

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.2+
- SQLite (default) or PostgreSQL/MySQL

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mOdoo
   ```

2. **Create virtual environment**
   ```bash
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # Choose appropriate requirements file
   pip install -r linux-requirement.txt  # Linux
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open browser to `http://127.0.0.1:8000/`
   - Login your account
   - Navigate to `/modules/` to manage modules

## Usage Guide

### Module Management

1. **Access Module Management**
   - Login to the system
   - Navigate to `/modules/` or click "Module Management"

2. **Install a Module**
   - Click "Install" button next to desired module
   - System will automatically:
     - Create database tables
     - Set up permissions
     - Register URLs
     - Enable module access

3. **Access Module Features**
   - Click "Open Module" to access installed modules
   - Example: `/product/` for product management, `/hr/` for HR management

### User Management

1. **Create Users**
   - Assign users to appropriate groups

2. **Group Permissions**
   - **manager**: Full access to all modules
   - **user**: Limited access (view/add/change, no delete)
   - **public**: Read-only access
   - **group_access_hr**: HR module access
   - **group_access_product**: Product module access

## Module Development

### Creating a New Module

1. **Create module directory structure**
   ```bash
   mkdir -p modules/your_module/templates
   touch modules/your_module/__init__.py
   ```

2. **Create core files following the established patterns**

   **models.py** - Define your data models
   ```python
   from django.db import models

   class YourModel(models.Model):
       name = models.CharField(max_length=100)
       description = models.TextField(blank=True)
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)

       def __str__(self):
           return self.name
   ```

   **services.py** - Business logic layer
   ```python
   from django.http import JsonResponse
   from .models import YourModel

   class YourService:
       @staticmethod
       def process_get(request, json_request):
           action = json_request.get('action')
           if action == 'list':
               return YourService.list_items(request)
           return JsonResponse({'success': False, 'message': 'Unknown action'})

       @staticmethod
       def process_post(request, json_request):
           action = json_request.get('action')
           if action == 'create':
               return YourService.create_item(request, json_request)
           return JsonResponse({'success': False, 'message': 'Unknown action'})
   ```

   **views.py** - Page and API views
   ```python
   from django.views import View
   from django.contrib.auth.mixins import PermissionRequiredMixin
   from .services import YourService

   class APIView(View):
       def post(self, request):
           import json
           json_request = json.loads(request.body.decode('utf-8'))
           return YourService.process_post(request, json_request)

   class YourPageView(PermissionRequiredMixin, View):
       permission_required = 'your_module.view_yourmodel'
       group_required = 'group_access_your_module'

       def get(self, request):
           from django.shortcuts import render
           return render(request, 'your_template.html')
   ```

   **urls.py** - URL routing
   ```python
   from django.urls import path
   from . import views

   urlpatterns = [
       path('', views.YourPageView.as_view(), name='your_module_index'),
       path('api/', views.APIView.as_view(context='your_api'), name='your_api'),
   ]
   ```

   **apps.py** - Permission setup
   ```python
   from django.apps import AppConfig

   class YourModuleConfig(AppConfig):
       name = 'modules.your_module'
       label = 'your_module'

       def ready(self):
           from django.contrib.auth.models import Group, Permission
           from django.contrib.contenttypes.models import ContentType
           from .models import YourModel

           content_type = ContentType.objects.get_for_model(YourModel)
           permissions = [
               Permission.objects.get_or_create(
                   codename='view_yourmodel',
                   name='Can view your model',
                   content_type=content_type,
               )[0],
               # Add other permissions (add, change, delete)
           ]

           manager_group, _ = Group.objects.get_or_create(name='manager')
           for p in permissions:
               manager_group.permissions.add(p.id)
   ```

3. **Create templates with consistent styling**
   - Create HTML templates in `templates/` directory
   - Use Tailwind CSS classes for consistent styling
   - Include necessary components (forms, tables, modals)

4. **Install and test**
   - Module auto-discovered on server restart
   - Install via `/modules/` interface
   - Access at `/your_module/`



### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## **Note**: This is a comprehensive Django-based ERP system designed for modularity and extensibility. Built to demonstrate modern Django development practices including service layers, API-driven architecture, role-based access control, and dynamic module loading.