from booster.adapters.manager.base import BaseManager
from booster.adapters.manager.npm import NpmManager


def get_manager(project_manager: str) -> BaseManager:
    if project_manager == "npm":
        return NpmManager
    else:
        raise ValueError(f"Invalid project manager: {project_manager}")
