INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOCAL_APPS = [
    'apps.site_config',
    'apps.site_identity',
{% if cookiecutter.use_blog_app == 'yes' %}    'apps.blog',{% endif %}
{% if cookiecutter.use_shop_app == 'yes' %}    'apps.shop',{% endif %}
{% if cookiecutter.use_newsletter_app == 'yes' %}    'apps.newsletter',{% endif %}
{% if cookiecutter.use_todo_app == 'yes' %}    'apps.todo',{% endif %}
] 