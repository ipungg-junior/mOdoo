# mOdoo - Modular Django ERP System

mOdoo is a minimal Django-based Enterprise Resource Planning (ERP) system that allows dynamic loading and management of business modules.

## Features

### Core Engine
- **Dynamic Module Management**: Install, uninstall, and upgrade modules at runtime
- **Permission-Based Access Control**: Role-based permissions with group management

### Available Modules 
- **Product Management**: Inventory management with CRUD operations
- **HR Management**: Employee management with user integration
- **Extensible Architecture**: Easy to add new business modules
## Architecture

### Project Structure
```
mOdoo/
├── engine/                 # Core application engine
│   ├── models.py          # Management models
│   ├── views.py           # Management views
│   ├── urls.py            # Core URL patterns
│   ├── apps.py            # Dynamic permission creation
│   └── templates/         # Core templates
├── modules/                # Base modules directory
│   ├── product/           # Product module
│   ├── hr/                # HR module
│   └── updater.py         # Module utilities / controller
├── mOdoo/                 # Django project settings
└── manage.py              # Django management script
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.2+

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ipungg-junior/mOdoo
   cd mOdoo
   ```

2. **Running virtual environment**
   ```bash
   source env/bin/activate 
   # For windows platform please activate from win-env '.\win-env\env\Script\activate'
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python3 manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python3 manage.py runserver --noreload
   ```

## Module Development

### Creating a New Module

1. **Create module directory**
   ```bash
   mkdir modules/your_module
   touch modules/your_module/__init__.py
   ```

2. **Create required files**
   ```python
   # modules/your_module/models.py
   from django.db import models

   class YourModel(models.Model):
       name = models.CharField(max_length=100)
       # Add your fields
   ```

   ```python
   # modules/your_module/views.py
   from django.views import View
   from django.contrib.auth.mixins import PermissionRequiredMixin

   class YourView(PermissionRequiredMixin, View):
       permission_required = ['engine.access_your_module', 'your_module.view_yourmodel']
       # Implement your views
   ```

   ```python
   # modules/your_module/urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path('', views.YourView.as_view(), name='your_view'),
   ]
   ```

3. **Add permissions in apps.py**
   ```python
   # modules/your_module/apps.py
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
                   name='Can view yourmodel',
                   content_type=content_type,
               )[0],
               # Add other permissions
           ]

           # Create groups and assign permissions
           manager_group, _ = Group.objects.get_or_create(name='manager')
           for p in permissions:
               manager_group.permissions.add(p.id)
   ```

4. **Restart server and install module**
   - The module will be automatically discovered
   - Install through the web interface



### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## **Note**: This is django test for recruitment purpose.