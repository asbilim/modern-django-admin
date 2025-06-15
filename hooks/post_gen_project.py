import os
import shutil

def remove_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def main():
    if '{{ cookiecutter.use_blog_app }}' == 'no':
        remove_dir('apps/blog')

    if '{{ cookiecutter.use_todo_app }}' == 'no':
        remove_dir('apps/todo')

if __name__ == '__main__':
    main() 