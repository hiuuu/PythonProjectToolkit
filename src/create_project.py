#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path
import yaml  # Requires PyYAML: pip install pyyaml

TEMPLATES = {
    "basic": {
        "dirs": ["src", "tests", "docs"],
        "files": {
            "src/main.py": "# Main application entry point\n",
            ".gitignore": (
                "# Python\n__pycache__/\n*.py[cod]\n*.so\n.Python\nbuild/\n"
                "develop-eggs/\ndist/\n*.egg-info/\n.installed.cfg\noutput/\n"
                "# Environment\n.env\n.venv/\nenv/\nvenv/\n"
            ),
            "README.md": (
                f"# {{project_name}}\n\nA new Python project\n\n"
                "## Installation\n\n```\npip install -r requirements.txt\n```\n"
            ),
            "requirements.txt": "# Project dependencies\n",
            "setup.py": (
                "from setuptools import setup\n\n"
                "setup(\n    name='{{project_name}}',\n    version='0.1',\n"
                "    packages=[],\n    install_requires=[],\n)\n"
            )
        }
    },
    "web": {
        "dirs": ["app", "tests", "static", "templates"],
        "files": {
            "app/__init__.py": "# Flask application\nfrom flask import Flask\napp = Flask(__name__)",
            "requirements.txt": "flask\npython-dotenv",
            ".env": "FLASK_APP=app\nFLASK_ENV=development"
        }
    },
    "data-science": {
        "dirs": ["notebooks", "data", "models"],
        "files": {
            "requirements.txt": "numpy\npandas\nmatplotlib\nscikit-learn",
            "analysis.py": "# Data analysis entry point\n"
        }
    }
}

def create_project(project_name, base_dir, template="basic", config_file=None, 
                  init_git=False, create_venv=False):
    project_path = base_dir / project_name
    project_path.mkdir(exist_ok=False)
    
    # Load configuration
    config = TEMPLATES[template]
    if config_file:
        with open(config_file) as f:
            custom_config = yaml.safe_load(f)
        config = merge_configs(config, custom_config)

    # Create structure
    create_directories(project_path, config["dirs"])
    create_files(project_path, config["files"], project_name)

    # Additional features
    if init_git:
        initialize_git(project_path)
    if create_venv:
        create_virtualenv(project_path)

    return project_path

def merge_configs(base_config, custom_config):
    """Merge template and custom configurations"""
    merged = {
        "dirs": list(set(base_config.get("dirs", []) + custom_config.get("dirs", []))),
        "files": {**base_config.get("files", {}), **custom_config.get("files", {})}
    }
    return merged

def create_directories(project_path, dirs):
    for d in dirs:
        dir_path = project_path / d
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "__init__.py").touch()

def create_files(project_path, files, project_name):
    for file_path, content in files.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        content = content.replace("{{project_name}}", project_name)
        full_path.write_text(content)

def initialize_git(project_path):
    try:
        subprocess.run(["git", "init", project_path], check=True)
        subprocess.run(["git", "-C", str(project_path), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(project_path), "commit", "-m", "Initial commit"],
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Git initialization failed: {str(e)}")

def create_virtualenv(project_path):
    venv_dir = project_path / "venv"
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"Virtual environment created at {venv_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Virtual environment creation failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Create enhanced Python project structure",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument("-d", "--dir", type=Path, default=Path.cwd(),
                      help="Base directory")
    parser.add_argument("-t", "--template", choices=TEMPLATES.keys(), default="basic",
                      help="Project template to use")
    parser.add_argument("-c", "--config", type=Path, 
                      help="Custom YAML config file path")
    parser.add_argument("-g", "--git", action="store_true",
                      help="Initialize Git repository")
    parser.add_argument("-v", "--venv", action="store_true",
                      help="Create virtual environment")
    parser.add_argument("--requirements", type=str,
                      help="Specify requirements (comma-separated)")

    args = parser.parse_args()

    try:
        project_path = create_project(
            args.name,
            args.dir,
            template=args.template,
            config_file=args.config,
            init_git=args.git,
            create_venv=args.venv
        )
        
        if args.requirements:
            add_requirements(project_path, args.requirements.split(","))

        print(f"Project created successfully at: {project_path}")

    except FileExistsError:
        print(f"Error: Directory '{args.name}' already exists in {args.dir}")
    except Exception as e:
        print(f"Error creating project: {str(e)}")

def add_requirements(project_path, packages):
    req_file = project_path / "requirements.txt"
    with req_file.open("a") as f:
        f.write("\n".join(packages) + "\n")

if __name__ == "__main__":
    main()
    
"""
# Full-featured example
python create_project.py awesome_project \
  --template web \
  --config custom_config.yaml \
  --git \
  --venv \
  --requirements "flask-sqlalchemy,celery"
"""