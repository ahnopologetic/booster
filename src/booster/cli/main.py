from __future__ import annotations
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import click
from booster.adapters.manager.base import BaseManager
from booster.adapters.manager.utils import get_manager

TEMPLATES_DIR = Path("templates")
RESERVED_NAMES = ["booster", "template", "config"]


def validate_template_name(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    if not value:
        raise click.BadParameter("Template name is required")

    if "/" in value or "\\" in value:
        raise click.BadParameter(
            f"Invalid template name: {value}. Template name cannot contain slashes."
        )

    if value.lower() in RESERVED_NAMES:
        raise click.BadParameter(f"Reserved template name: {value}")

    return value


def load_booster_config(template_name: str) -> dict[str, Any]:
    template_dir: Path = TEMPLATES_DIR / template_name
    config_path: Path = template_dir / "booster.json"

    if not template_dir.exists():
        raise click.BadParameter(f"Template not found: {template_name}")

    if not config_path.exists():
        raise click.BadParameter(f"Template config not found: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


def parse_variable(variable_str: str) -> tuple[str, str]:
    if "=" not in variable_str:
        raise click.BadParameter(
            f"Invalid variable format: {variable_str}. Expected format: name=value"
        )

    name, value = variable_str.split("=", 1)
    return name, value


def ensure_template_dir_exists():
    if not TEMPLATES_DIR.exists():
        TEMPLATES_DIR.mkdir(parents=True)


@click.group()
def main():
    """Booster - A template-based project generator."""
    pass


@main.command()
@click.argument("template_name", callback=validate_template_name)
@click.option(
    "--project-manager",
    "-p",
    type=click.Choice(["npm", "uv", "bun"]),
    help="Project manager to use",
    default="npm",
)
@click.option(
    "--variable",
    "-v",
    multiple=True,
    help="Define a variable for the template (format: name=type)",
)
def new(template_name: str, variable: list[str], project_manager: str | None = None):
    """Create a new template."""
    ensure_template_dir_exists()
    template_dir = TEMPLATES_DIR / template_name

    if template_dir.exists():
        raise click.BadParameter(f"Template already exists: {template_name}")

    template_dir.mkdir(parents=True)

    # Create booster.json config
    variables = {}
    for var in variable:
        name, var_type = parse_variable(var)
        variables[name] = {
            "type": var_type,
            "description": f"{name} variable",
            "default": "",
        }

    config: dict[str, Any] = {
        "name": template_name,
        "description": f"A {template_name} template",
        "version": "1.0.0",
        "variables": variables,
        "project_manager": project_manager,
    }

    with open(template_dir / "booster.json", "w") as f:
        json.dump(config, f, indent=2)

    click.echo(f"Created template: {template_name}")


@main.command()
@click.argument("template_name")
@click.argument("project_name")
@click.option(
    "--force/--no-force",
    default=False,
    help="Force creation even if project already exists",
)
@click.option(
    "--variable",
    "-v",
    multiple=True,
    help="Override variables for the template (format: name=value)",
)
def create(
    template_name: str,
    project_name: str,
    force: bool,
    variable: list[str],
):
    """Create a project from a template."""
    ensure_template_dir_exists()
    project_dir = Path(project_name)

    # Check if template exists
    template_dir = TEMPLATES_DIR / template_name
    template_source_dir = template_dir / "project"

    if not template_dir.exists():
        raise click.BadParameter(f"Template not found: {template_name}")

    # Check if project already exists
    if project_dir.exists():
        if not force:
            raise click.BadParameter(
                f"Project directory already exists: {project_name}"
            )
        shutil.rmtree(project_dir)

    # Load template config
    config = load_booster_config(template_name)

    # Process variables
    template_vars = config.get("variables", {})
    var_values = {k: v.get("default", "") for k, v in template_vars.items()}

    # Override with user-provided variables
    for var in variable:
        name, value = parse_variable(var)
        if name not in template_vars:
            raise click.BadParameter(f"Unknown variable: {name}")
        var_values[name] = value

    # Create project directory
    project_dir.mkdir(parents=True)

    project_manager = config["project_manager"]

    # TODO: Add support for other project managers
    manager: BaseManager = get_manager(project_manager)(
        project_dir, template_source_dir
    )
    manager.validate_project()
    manager.copy_files()

    # Process template_paths from config
    for _, path_template in config.get("template_paths", {}).items():
        # Replace variables in path
        for var_name, var_value in var_values.items():
            path_template = path_template.replace(f"{{{{ {var_name} }}}}", var_value)

        # Create directory
        target_path = project_dir / path_template
        target_path.mkdir(parents=True, exist_ok=True)

    # Run post-create hooks if any
    post_create_hook = config.get("hooks", {}).get("post_create")
    if post_create_hook:
        os.system(post_create_hook)

    click.echo(f"Created project: {project_name} from template: {template_name}")


@main.command()
@click.argument("template_name")
def show(template_name: str):
    """Show template details."""
    try:
        config = load_booster_config(template_name)
        click.echo(f"Template: {config.get('name', template_name)}")
        click.echo(f"Description: {config.get('description', '')}")
        click.echo(f"Version: {config.get('version', '')}")

        if "variables" in config:
            click.echo("\nVariables:")
            for name, details in config["variables"].items():
                click.echo(f"  {name}:")
                click.echo(f"    Description: {details.get('description', '')}")
                click.echo(f"    Type: {details.get('type', '')}")
                click.echo(f"    Default: {details.get('default', '')}")
    except click.BadParameter as e:
        click.echo(str(e), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
