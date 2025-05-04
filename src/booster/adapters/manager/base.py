from pathlib import Path
import shutil


class BaseManager:
    def __init__(
        self, project_dir: Path, template_dir: Path, files_to_ignore: list[str]
    ):
        self.project_dir = project_dir
        self.template_dir = template_dir
        self.files_to_ignore = files_to_ignore

    def validate_project(self):
        raise NotImplementedError("Subclasses must implement this method")

    def install_dependencies(self):
        raise NotImplementedError("Subclasses must implement this method")

    def copy_files(self):
        for item in self.template_dir.glob("*"):
            if item.name == "booster.json":
                continue

            if item.name in self.files_to_ignore:
                continue

            if item.is_dir():
                shutil.copytree(item, self.project_dir / item.name)
            else:
                shutil.copy2(item, self.project_dir / item.name)

    def run_hook(self, hook_name: str):
        raise NotImplementedError("Subclasses must implement this method")
