# Blog API Integration Guide

This guide provides detailed instructions for integrating a frontend application with the built-in Blog API. It covers the core endpoints, authentication, and the internationalization (i18n) system for retrieving translated content.

## Core Concepts

### Internationalization (i18n) and Language Selection

The Blog API is fully internationalized, allowing you to retrieve translated content for models like **Posts** and **Categories**. All translated fields (`title`, `content`, `slug`, `excerpt`, etc.) will automatically be returned in the language specified by the frontend client.

**To request content in a specific language, you must include the `Accept-Language` HTTP header in your API request.**

The supported language codes are:

- `en` (English)
- `de` (German)
- `fr` (French)

If no language is specified, the API will fall back to the default language, which is English (`en`).

**Example: Fetching Posts in French**

```http
GET /api/blog/posts/
Accept: application/json
Accept-Language: fr
```

The response will contain all posts with their `title`, `excerpt`, and `slug` fields translated into French.

**Example Response (truncated):**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "c2a9a3f2-8c8e-4b9f-b3a1-5f0e1c2d3a4b",
      "title": "Mon Premier Article de Blog", // Translated
      "slug": "mon-premier-article-de-blog", // Translated
      "excerpt": "Ceci est un bref résumé de l'article...", // Translated
      "author": { ... },
      "published_at": "2023-10-28T12:00:00Z",
      ...
    }
  ]
}
```

This system applies to all `GET` requests for translatable content, including single posts, categories, and tags.

### Managing Translated Content

This guide focuses on **reading** content from the public-facing blog API. The process for **creating and editing** translated content in the admin panel is different.

For a detailed explanation of how to build a frontend that can manage translated fields (e.g., showing `title_en`, `title_de`, and `title_fr` in a tabbed interface), please refer to the **[API Integration Guide](./API_INTEGRATION_GUIDE.md)**.

### Permissions

- **Public Access**: Most `GET` endpoints (reading posts, categories, tags, comments) are public and do not require authentication.
- **Authenticated Actions**: Actions like creating a comment, liking/unliking a post, or subscribing to the newsletter require a valid JWT token in the `Authorization` header.

## Main Endpoints

### Posts

- **Endpoint**: `/api/blog/posts/`
- **Model**: `Post`

#### List Posts: `GET /api/blog/posts/`

Returns a paginated list of all published posts.

- **Query Parameters**:
  - `page`: The page number for pagination.
  - `search`: A search term to filter posts by `title`, `content`, or `excerpt`.
  - `ordering`: Fields to order by, e.g., `published_at`, `-view_count`.

##### **Post List Response Fields**

Each item in the `results` array will have the following structure:

```json
{
  "id": "c2a9a3f2-8c8e-4b9f-b3a1-5f0e1c2d3a4b",
  "title": "My First Blog Post",
  "slug": "my-first-blog-post",
  "excerpt": "This is a short summary of the post...",
  "author": {
    "id": 1,
    "username": "admin",
    "first_name": "Paul",
    "last_name": "Lilian",
    "email": "admin@example.com",
    "post_count": 15
  },
  "categories": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "All about tech.",
      "parent": null,
      "is_active": true,
      "post_count": 5,
      "meta_title": "Tech Category",
      "meta_description": "...",
      "subcategories": []
    }
  ],
  "tags": [
    {
      "id": 1,
      "name": "Django",
      "slug": "django",
      "color": "#092E20",
      "post_count": 3
    }
  ],
  "featured_image": "/media/blog/posts/my-first-blog-post/featured_image/image.jpg",
  "is_featured": true,
  "is_sticky": false,
  "published_at": "2023-10-28T12:00:00Z",
  "reading_time": 5,
  "view_count": 1024,
  "likes_count": 128,
  "comments_count": 16,
  "absolute_url": "http://localhost:8000/blog/my-first-blog-post/"
}
```

#### Retrieve a Post: `GET /api/blog/posts/<uuid>/`

Returns a single post with all its details, including the full `content`, `meta_data`, and related posts. Remember to include the `Accept-Language` header to get the translated version.

##### **Post Detail Response Fields**

The response for a single post includes all the fields from the list view, plus the following:

```json
{
  "id": "c2a9a3f2-8c8e-4b9f-b3a1-5f0e1c2d3a4b",
  "title": "My First Blog Post",
  "slug": "my-first-blog-post",
  "excerpt": "This is a short summary of the post...",
  "author": {
    "id": 1,
    "username": "admin",
    "first_name": "Paul",
    "last_name": "Lilian",
    "email": "admin@example.com",
    "post_count": 15
  },
  "categories": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "All about tech.",
      "parent": null,
      "is_active": true,
      "post_count": 5,
      "meta_title": "Tech Category",
      "meta_description": "...",
      "subcategories": []
    }
  ],
  "tags": [
    {
      "id": 1,
      "name": "Django",
      "slug": "django",
      "color": "#092E20",
      "post_count": 3
    }
  ],
  "featured_image": "/media/blog/posts/my-first-blog-post/featured_image/image.jpg",
  "is_featured": true,
  "is_sticky": false,
  "published_at": "2023-10-28T12:00:00Z",
  "reading_time": 5,
  "view_count": 1024,
  "likes_count": 128,
  "comments_count": 16,
  "absolute_url": "http://localhost:8000/blog/my-first-blog-post/",
  "content": "<h1>This is the full post content</h1><p>It can contain rich HTML or Markdown...</p>",
  "meta_title": "Meta Title for SEO",
  "meta_description": "Meta description for SEO.",
  "meta_keywords": "django, react, api",
  "og_image": "/media/blog/posts/my-first-blog-post/og_image/og_image.jpg",
  "previous_post": {
    "id": "a1b2c3d4-...",
    "title": "The Post Before This One",
    "slug": "the-post-before-this-one"
  },
  "next_post": null,
  "related_posts": [
    {
      "id": "e5f6g7h8-...",
      "title": "A Similar Post in the Same Category",
      "slug": "a-similar-post"
    }
  ]
}
```

#### Post Actions (Authenticated)

- **Like a Post**: `POST /api/blog/posts/<uuid>/like/`
  - Adds the authenticated user to the list of users who liked the post.
- **Unlike a Post**: `POST /api/blog/posts/<uuid>/unlike/`
  - Removes the authenticated user's like.
- **Increment View Count**: `POST /api/blog/posts/<uuid>/increment_view/`
  - A public endpoint to increment the `view_count`. This should be called by the frontend whenever a post is viewed.

### Categories

- **Endpoint**: `/api/blog/categories/`
- **Model**: `Category`

#### List Categories: `GET /api/blog/categories/`

Returns a list of all active categories. The `name`, `description`, and `slug` are translatable.

#### Retrieve Category Posts: `GET /api/blog/categories/<id>/posts/`

Returns a paginated list of all published posts belonging to that specific category.

### Tags & Authors

- **Tags**: `GET /api/blog/tags/`
  - Works similarly to categories.
- **Authors**: `GET /api/blog/authors/`
  - Returns a list of users (authors). You can get all posts for a specific author via `GET /api/blog/authors/<id>/posts/`.

## Interacting With Posts

### Comments

- **Endpoint**: `/api/blog/posts/<post_uuid>/comments/`

#### List Comments for a Post: `GET /api/blog/posts/<post_uuid>/comments/`

Returns a paginated list of approved, top-level comments for a specific post. Nested replies are included in the `replies` field of each comment.

#### Create a Comment: `POST /api/blog/posts/<post_uuid>/comments/` (Authenticated)

Creates a new comment on a post.

- **Request Body**:

```json
{
  "content": "This is a great article!",
  "parent": null // or the UUID of the comment you are replying to
}
```

If the user is not authenticated, `author_name` and `author_email` fields are required.

## Utility Endpoints

### Search

- **Endpoint**: `GET /api/blog/search/`
- **Query Parameter**: `q`
- **Example**: `GET /api/blog/search/?q=django`
- Returns a paginated list of posts matching the search query.

### Blog Stats

- **Endpoint**: `GET /api/blog/stats/`
- Returns a simple JSON object with statistics like total posts, comments, categories, and tags.

### Newsletter Subscription

- **Endpoint**: `POST /api/blog/newsletter/`
- **Request Body**:

```json
{
  "email": "subscriber@example.com"
}
```

Subscribes a new email address to the newsletter.
