# API Integration & Frontend Guide

This guide provides detailed instructions for integrating a frontend application with the Django Admin API. It covers the overall architecture, authentication, and how to use the dynamic metadata provided by the API to build a rich user interface.

## Core Concepts

The API is designed to be self-describing. Instead of hardcoding forms and views on the frontend, you should fetch the configuration from the backend and render the UI dynamically. This makes your frontend automatically adapt to changes in the backend models.

- **Primary Keys as UUIDs**: All models use UUIDs as primary keys. When making API requests for a specific object, you will use its UUID string in the URL (e.g., `/api/admin/models/post/<uuid>/`). The `id` field in all API responses will be a UUID string.

- **Dynamic Endpoints**: The API automatically generates endpoints for all models registered in the Django admin. You don't need to know the model names beforehand.

- **Metadata-Driven UI**: The API provides rich metadata about each model, including its fields, validation rules, and suggested UI components for rendering. This allows you to build a generic frontend that can handle any model.

## 1. Fetching Site Configuration

The first step is to get a list of all manageable models and general site configuration.

- **Endpoint**: `GET /api/admin/`
- **Authentication**: Requires admin user token.
- **What it returns**: A JSON object containing all registered models, grouped by category, and a set of `frontend_options` like predefined icons and categories.

**Example Response (`/api/admin/`)**:

```json
{
  "models": {
    "blog.Post": {
      "app_label": "blog",
      "model_name": "post",
      "verbose_name": "Post",
      "verbose_name_plural": "Posts",
      "category": "Blog",
      "frontend_config": {
        "icon": "file-text",
        "color": "#3B82F6",
        "description": "Manage blog posts, articles, and news.",
        "include_in_dashboard": true
      },
      "api_url": "/api/admin/models/post/"
    }
    // ... other models
  },
  "categories": {
    "Blog": ["blog.Post", "blog.Comment", "core.Category", "core.Tag"],
    "Access Control": ["auth.User", "auth.Group"]
    // ... other categories
  },
  "frontend_options": {
    "categories": ["Access Control", "Blog", "Site Settings"],
    "icons": ["user", "file-text", "settings", "..."]
  }
}
```

**Frontend Implementation**:

1. On dashboard load, fetch from this endpoint.
2. Use the `categories` and `models` data to build your main navigation menu (e.g., a sidebar). Each item should link to a generic list view page, like `/admin/[modelName]`.
3. Store the `frontend_options` in your app's state or context to populate dropdowns for icons or categories when creating/editing models that have these fields.

## 2. Fetching Model-Specific Configuration (The "Recipe")

Once the user navigates to a model's list page (e.g., `/admin/post`), you need to fetch the "recipe" for that model to know how to display its data and build its forms.

- **Endpoint**: `GET /api/admin/models/<model-name>/config/`
- **Example**: `GET /api/admin/models/post/config/`
- **Authentication**: Requires admin user token.
- **What it returns**: Detailed configuration for the specified model, including a list of all its fields, admin settings (`list_display`), and user permissions.

**Example Response (`/api/admin/models/post/config/`)**:

```json
{
  "model_name": "post",
  "verbose_name": "Post",
  "verbose_name_plural": "Posts",
  "fields": {
    "title": { "name": "title", "type": "CharField", "ui_component": "textfield", "required": true, "is_translation": true, ... },
    "content": { "name": "content", "type": "TextField", "ui_component": "markdown_editor", "required": false, "is_translation": true, ... },
    "status": { "name": "status", "type": "CharField", "ui_component": "select", "choices": [{"value": "draft", "label": "Draft"}, {"value": "published", "label": "Published"}], ... },
    "author": { "name": "author", "type": "ForeignKey", "ui_component": "foreignkey_select", "related_model": { "api_url": "/api/admin/models/user/" }, ... },
    "tags": { "name": "tags", "type": "ManyToManyField", "ui_component": "manytomany_select", "related_model": { "api_url": "/api/admin/models/tag/" }, ... }
  },
  "admin_config": {
    "list_display": ["title", "author", "status", "published_at"],
    "search_fields": ["title", "content"]
  },
  "permissions": { "add": true, "change": true, "delete": true, "view": true }
}
```

**Frontend Implementation**:

- Use `admin_config.list_display` to determine which columns to show in your data table.
- Use `admin_config.search_fields` to know which fields to include in a search query.
- When a user clicks "Create" or "Edit", use the `fields` object to dynamically generate a form:
  - Iterate through the `fields` object.
  - For each field, use the `ui_component` value to render the appropriate React component (e.g., `<TextField />`, `<SelectField />`, `<MarkdownEditor />`).
  - Pass the other metadata (`verbose_name` as label, `help_text`, `required`, `choices`, etc.) as props to your component.
- The `is_translation: true` flag indicates that you should render fields for each supported language (e.g., `title_en`, `title_de`, `title_fr`), perhaps in a tabbed interface.

## 3. CRUD Operations

Once you have the model's config, you can perform standard CRUD.

- **List (GET)**: `GET /api/admin/models/<model-name>/` (Supports pagination, filtering, searching, ordering)
- **Retrieve (GET)**: `GET /api/admin/models/<model-name>/<uuid>/`
- **Create (POST)**: `POST /api/admin/models/<model-name>/`
- **Update (PUT/PATCH)**: `PUT /api/admin/models/<model-name>/<uuid>/`
- **Delete (DELETE)**: `DELETE /api/admin/models/<model-name>/<uuid>/`

## 4. Special UI Components

### Markdown Editor

- **Hint**: `ui_component: 'markdown_editor'`
- When your form builder encounters a field with this component hint, it should render a rich text editor that supports Markdown (e.g., `react-markdown`, `easymde`, or a custom component with a preview).
- The value sent to the API should be the raw Markdown string. The backend will handle processing it.

### Foreign Key & ManyToMany

- **Hint**: `ui_component: 'foreignkey_select'` or `'manytomany_select'`
- The field metadata will include a `related_model` object with an `api_url`.
- Your frontend component should:
  1. Fetch data from the `related_model.api_url` (e.g., `/api/admin/models/user/`) to get a list of possible items to link.
  2. Render a searchable dropdown or a multi-select box.
  3. For a `ForeignKey`, submit the UUID of the selected item.
  4. For a `ManyToManyField`, submit an array of UUIDs of the selected items.

## 5. Dashboard Statistics

A special endpoint is available to populate a dashboard with analytics and recent activity.

- **Endpoint**: `GET /api/admin/dashboard-stats/`
- **Authentication**: Requires admin user token.
- **What it returns**: A consolidated object with data perfect for dashboard widgets.

**Example Response (`/api/admin/dashboard-stats/`)**:

```json
{
  "stats": [
    {
      "title": "Total Users",
      "value": "1,234",
      "change": "+56",
      "icon": "users",
      "description": "Since last 30 days"
    },
    {
      "title": "Total Posts",
      "value": "567",
      "change": "+12",
      "icon": "file-text",
      "description": "Published in last 30 days"
    }
  ],
  "user_signups_over_time": [
    { "date": "Jan", "count": 100 },
    { "date": "Feb", "count": 150 }
  ],
  "content_creation_stats": [
    { "name": "Posts", "value": 567 },
    { "name": "Comments", "value": 2048 },
    { "name": "Projects", "value": 42 }
  ],
  "activity_feed": [
    {
      "type": "new_post",
      "title": "New Post: \"My Awesome Adventure\"",
      "user": "admin",
      "timestamp": "2023-10-27T10:00:00Z"
    },
    {
      "type": "new_comment",
      "title": "New comment on \"My Awesome Adventure\"",
      "user": "Jane Doe",
      "timestamp": "2023-10-27T10:30:00Z"
    }
  ]
}
```

**Frontend Implementation**:

- Fetch this data on your main dashboard page.
- `stats`: Use this array to create top-level statistic cards.
- `user_signups_over_time`: Use this data to render a line or bar chart showing user growth.
- `content_creation_stats`: Use this to render a pie or donut chart showing the distribution of content types.
- `activity_feed`: Use this to display a "Recent Activity" or "What's New" widget.
