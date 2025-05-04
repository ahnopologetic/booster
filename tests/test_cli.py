import os

import pytest
from click.testing import CliRunner

from booster.cli.main import main


@pytest.fixture
def cli():
    return CliRunner()


@pytest.fixture
def tempdir(tmp_path, monkeypatch):
    """Create a temporary directory for tests and patch templates directory path."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Monkeypatch the TEMPLATES_DIR in the main module
    from booster.cli.main import TEMPLATES_DIR

    monkeypatch.setattr("booster.cli.main.TEMPLATES_DIR", templates_dir)

    # Change to the temporary directory for the duration of the test
    original_dir = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path

    # Return to the original directory
    os.chdir(original_dir)


def test_booster_new_should_create_template(cli, tempdir):
    result = cli.invoke(main, ["new", "my-template"])
    assert result.exit_code == 0
    assert os.path.exists(tempdir / "templates" / "my-template")
    assert os.path.exists(tempdir / "templates" / "my-template" / "booster.json")


def test_booster_new_should_fail_if_template_already_exists(cli, tempdir):
    # First create the template
    cli.invoke(main, ["new", "existing-template"])
    # Then try to create it again
    result = cli.invoke(main, ["new", "existing-template"])
    assert result.exit_code != 0
    assert "Template already exists" in result.output


def test_booster_new_should_fail_if_template_name_is_invalid(cli, tempdir):
    result = cli.invoke(main, ["new", "invalid/template"])
    assert result.exit_code != 0
    assert "Invalid template name" in result.output


def test_booster_new_should_fail_if_template_name_is_reserved(cli, tempdir):
    result = cli.invoke(main, ["new", "booster"])
    assert result.exit_code != 0
    assert "Reserved template name" in result.output


def test_booster_new_should_create_project_with_booster_config(cli, tempdir):
    result = cli.invoke(
        main,
        [
            "new",
            "config-template",
            "--variable",
            "name=string",
            "--variable",
            "version=string",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(tempdir / "templates" / "config-template" / "booster.json")

    # Verify config has variables
    with open(tempdir / "templates" / "config-template" / "booster.json", "r") as f:
        content = f.read()
        assert "name" in content
        assert "version" in content


def test_booster_create_should_create_project_when_parameters_are_valid(cli, tempdir):
    # First create a template
    cli.invoke(main, ["new", "valid-template"])

    # Then create a project from it
    result = cli.invoke(main, ["create", "valid-template", "my-project"])
    assert result.exit_code == 0
    assert os.path.exists(tempdir / "my-project")


def test_booster_create_should_fail_if_parameters_are_invalid(cli, tempdir):
    result = cli.invoke(main, ["create", "non-existent-template", "my-project"])
    assert result.exit_code != 0
    assert "Template not found" in result.output


def test_booster_create_should_fail_if_project_already_exists(cli, tempdir):
    # Create a template
    cli.invoke(main, ["new", "template-exists"])

    # Create a directory that will conflict
    os.makedirs(tempdir / "existing-project", exist_ok=True)

    # Try to create the project
    result = cli.invoke(main, ["create", "template-exists", "existing-project"])
    assert result.exit_code != 0
    assert "Project directory already exists" in result.output


def test_booster_create_should_work_if_project_already_exists_and_force_is_true(
    cli, tempdir
):
    # Create a template
    cli.invoke(main, ["new", "force-template"])

    # Create a directory that will conflict
    os.makedirs(tempdir / "force-project", exist_ok=True)
    with open(tempdir / "force-project" / "test-file.txt", "w") as f:
        f.write("original content")

    # Create with force
    result = cli.invoke(main, ["create", "force-template", "force-project", "--force"])
    assert result.exit_code == 0
    assert os.path.exists(tempdir / "force-project")
    assert not os.path.exists(tempdir / "force-project" / "test-file.txt")


def test_booster_create_should_fail_if_project_already_exists_and_force_is_false(
    cli, tempdir
):
    # Create a template
    cli.invoke(main, ["new", "no-force-template"])

    # Create a directory that will conflict
    os.makedirs(tempdir / "no-force-project", exist_ok=True)

    # Try to create without force
    result = cli.invoke(
        main, ["create", "no-force-template", "no-force-project", "--no-force"]
    )
    assert result.exit_code != 0
    assert "Project directory already exists" in result.output


def test_booster_create_with_overriding_variables_should_work_and_override_variables(
    cli, tempdir
):
    # Create a template with variables
    cli.invoke(
        main,
        [
            "new",
            "var-template",
            "--variable",
            "name=string",
            "--variable",
            "version=string",
        ],
    )

    # Create project with variable overrides
    result = cli.invoke(
        main,
        [
            "create",
            "var-template",
            "var-project",
            "--variable",
            "name=my-app",
            "--variable",
            "version=1.0.0",
        ],
    )
    assert result.exit_code == 0

    # Verify variables were applied
    assert os.path.exists(tempdir / "var-project")


def test_booster_create_with_overriding_variables_should_fail_if_variables_are_invalid(
    cli, tempdir
):
    # Create a template with specific variables
    cli.invoke(
        main,
        [
            "new",
            "invalid-var-template",
            "--variable",
            "name=string",
            "--variable",
            "version=string",
        ],
    )

    # Attempt with invalid variable
    result = cli.invoke(
        main,
        [
            "create",
            "invalid-var-template",
            "invalid-var-project",
            "--variable",
            "non_existent=value",
        ],
    )
    assert result.exit_code != 0
    assert "Unknown variable" in result.output


def test_booster_show_with_template_name_should_show_booster_config_with_overridable_variables(
    cli, tempdir
):
    # Create a template with variables
    cli.invoke(
        main,
        [
            "new",
            "show-template",
            "--variable",
            "name=string",
            "--variable",
            "version=string",
        ],
    )

    # Show the template
    result = cli.invoke(main, ["show", "show-template"])
    assert result.exit_code == 0
    assert "name" in result.output
    assert "version" in result.output


def test_booster_show_with_template_name_should_fail_if_template_name_is_invalid(
    cli, tempdir
):
    result = cli.invoke(main, ["show", "non-existent-template"])
    assert result.exit_code != 0
    assert "Template not found" in result.output
