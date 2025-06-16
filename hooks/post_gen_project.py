import os
import random
import string
import shutil

def generate_secret_key(length=50):
    """Generate a random secret key."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(random.choice(chars) for i in range(length))

def set_secret_key(project_directory):
    """Read .env.example, create .env, and set a new secret key."""
    env_example_path = os.path.join(project_directory, '.env.example')
    env_path = os.path.join(project_directory, '.env')

    if not os.path.exists(env_example_path):
        print(f"Warning: .env.example not found at {env_example_path}")
        return

    with open(env_example_path, 'r') as f:
        content = f.read()

    new_secret_key = generate_secret_key()
    # Assuming the placeholder in .env.example is 'your-secret-key-change-this'
    content = content.replace('your-secret-key-change-this', new_secret_key, 1)

    with open(env_path, 'w') as f:
        f.write(content)

def remove_dir(dir_path):
    """Remove a directory if it exists."""
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def main():
    project_directory = os.path.realpath(os.path.curdir)
    
    print("Generating secret key and creating .env file...")
    set_secret_key(project_directory)
    print("SUCCESS: .env file created.")

    if '{{ cookiecutter.use_blog_app }}' != 'yes':
        remove_dir(os.path.join(project_directory, 'apps/blog'))

    if '{{ cookiecutter.use_shop_app }}' != 'yes':
        remove_dir(os.path.join(project_directory, 'apps/shop'))

    if '{{ cookiecutter.use_newsletter_app }}' != 'yes':
        remove_dir(os.path.join(project_directory, 'apps/newsletter'))

    print("SUCCESS: Project setup complete.")

if __name__ == '__main__':
    main() 