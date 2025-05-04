# Booster

A template-based project generator that helps you quickly scaffold new projects based on predefined templates.

## Features

- Create and manage project templates
- Generate new projects from templates
- Define and customize template variables
- Validate template configurations
- Support for post-creation hooks

## Installation

```bash
pip install booster
-- for uvx user
uvx apg-booster 
```

For development:

```bash
# Clone the repository
git clone https://github.com/yourusername/booster.git
cd booster

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Creating a New Template

```bash
booster new my-template
```

With variables:

```bash
booster new my-template --variable name=string --variable version=string
```

### Creating a Project from a Template

```bash
booster create my-template my-project
```

With variable overrides:

```bash
booster create my-template my-project --variable name=awesome-app --variable version=1.0.0
```

### Viewing Template Details

```bash
booster show my-template
```

## Template Structure

Templates are stored in the `templates/` directory. Each template consists of:

- A `booster.json` configuration file
- Template files and directories to be copied to the new project

Example `booster.json`:

```json
{
  "name": "my-template",
  "description": "A template for awesome projects",
  "version": "1.0.0",
  "variables": {
    "name": {
      "type": "string",
      "description": "Project name",
      "default": "my-project"
    },
    "version": {
      "type": "string",
      "description": "Project version",
      "default": "0.1.0"
    }
  },
  "template_paths": {
    "src": "src/{{ name }}",
    "tests": "tests/{{ name }}"
  },
  "hooks": {
    "post_create": "echo 'Project created successfully!'"
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

Run tests using pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Click](https://click.palletsprojects.com/) for the command-line interface
