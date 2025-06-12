# Django Admin API

A modern Django admin interface with auto-generated REST API for any Django project.

Created by: **asbilim**

- **Twitter:** [@iampaullilian](https://twitter.com/iampaullilian)
- **GitHub:** [asbilim](https://github.com/asbilim)
- **Portfolio:** [paullilian.dev](https://paullilian.dev)

## Features

- **Auto-generated API:** Automatically creates REST API endpoints for all models registered in the Django admin.
- **Dynamic Configuration:** Manage site settings like email and file storage directly through the API.
- **User & Group Management:** Super admins can manage users and groups via the API.
- **Frontend Ready:** Provides configuration endpoints for easy integration with a frontend dashboard.
- **Customizable:** Easily extend and customize serializers, viewsets, and permissions.

## Quick Start

1. **Setup Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**

   Create a `.env` file from the example:

   ```bash
   cp .env.example .env
   ```

   Then, edit the `.env` file with your settings. See the `.env.example` file for detailed explanations of each variable.

4. **Database Setup**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- **Admin API Root**: `http://localhost:8000/api/admin/`
- **API for a model**: `http://localhost:8000/api/admin/models/<model-name>/`
- **Traditional Admin**: `http://localhost:8000/admin/`
- **API Schema**:
  - `http://localhost:8000/api/schema/` (Download OpenAPI Schema)
  - `http://localhost:8000/api/schema/swagger-ui/` (Swagger UI)
  - `http://localhost:8000/api/schema/redoc/` (Redoc)

## Project Structure

- `admin_api/` - The core app for the auto-generated admin API.
- `config/` - Django settings, main URL configuration, and WSGI entry point.
- `apps/` - Your project's applications (e.g., `core`, `blog`, `site_config`).
