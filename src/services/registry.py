from src.core.app_config import AppConfig


class ServiceRegistry:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
