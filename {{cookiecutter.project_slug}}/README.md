# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

Created by: **{{ cookiecutter.author_name }}**

- **Twitter:** [@iampaullilian](https://twitter.com/iampaullilian)
- **GitHub:** [asbilim](https://github.com/asbilim)
- **Portfolio:** [paullilian.dev](https://paullilian.dev)

## Features

- **Auto-generated API:** Automatically creates REST API endpoints for all models registered in the Django admin.
- **Dashboard Analytics:** A new `/api/admin/dashboard-stats/` endpoint provides a comprehensive overview of site activity, including user signups, content creation statistics, and recent activities.
- **Pre-built Blog App:** Includes a full-featured, RESTful blog API with posts, categories, tags, comments, and more.
- **Dynamic Configuration:** Manage site settings like email and file storage directly through the API.
- **Enhanced Site Identity:** More detailed site identity management, including author information, contact details, and social media links.
- **Admin User Preferences:** Users can have their own admin UI preferences, such as theme and layout density.
- **API Request Logging:** Automatically logs API requests for analytics and monitoring.
- **Site Identity & SEO:** Manage your site's name, logo, favicon, and SEO tags from a central place.
- **User & Group Management:** Super admins can manage users and groups via the API.
- **Frontend Ready:** Provides configuration endpoints for easy integration with a frontend dashboard.
- **Customizable:** Easily extend and customize serializers, viewsets, and permissions.
- **Automatic Translations:** All text fields are available in English, German and French. The public-facing APIs (like the Blog API) serve translated content based on the `Accept-Language` header. See the `BLOG_API_GUIDE.md` for more details.
- **UI Component Metadata:** Each API response includes suggested components for creating, editing and displaying fields, plus predefined choices for things like icons and categories to ensure a consistent look and feel.

## Quick Start

Your project has been successfully generated! To get it up and running, follow these steps from your terminal.

1.  **Navigate to Your Project Directory**

    ```bash
    cd {{ cookiecutter.project_slug }}
    ```

2.  **Setup The Virtual Environment**

    It's highly recommended to use a virtual environment to manage your project's dependencies.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Review Environment Variables**

    A `.env` file has been automatically created for you with a new `SECRET_KEY`. You may want to review this file and customize other settings (like database credentials) for your local environment.

5.  **Run Database Migrations**

    This will set up your project's database schema.

    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser**

    You'll need an admin account to access the dashboard.

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Development Server**

    ```bash
    python manage.py runserver
    ```

    Your new Django project is now running at `http://localhost:8000`.

## API Endpoints

- **Admin API Root**: `
