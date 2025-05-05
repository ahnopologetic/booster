from __future__ import annotations
from pathlib import Path

from adapters.manager.base import BaseManager

FILES_TO_IGNORE = [
    "package-lock.json",
    "node_modules",
    "booster.json",
]


class NpmManager(BaseManager):
    def __init__(
        self,
        project_dir: Path,
        template_dir: Path,
        files_to_ignore: list[str] | None = None,
    ):
        super().__init__(project_dir, template_dir, files_to_ignore or FILES_TO_IGNORE)

    def validate_project(self):
        # validate package.json
        ...
