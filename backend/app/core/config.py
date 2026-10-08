from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_version() -> str:
    version_file = Path(__file__).resolve().parents[3] / "VERSION"
    if version_file.is_file():
        content = version_file.read_text(encoding="utf-8").strip()
        if content:
            return content
    return "1.0.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "prompt-optimizer-alan-vo"
    app_version: str = load_version()
    environment: str = "development"
    demo_mode: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str = "prompt-optimizer-alan-vo-secret-key-at-least-32-chars-long"

    # SQLite persistent storage
    database_url: str = "sqlite:///./data/prompt_optimizer.db"

    # OIDC & Keycloak configuration
    oidc_issuer_url: str = "http://127.0.0.1:8080/realms/prompt-optimizer"
    oidc_client_id: str = "prompt-optimizer-client"
    oidc_audience: str = "prompt-optimizer-api"

    # LLM configuration (Keys only server-side)
    llm_api_key: str | None = None
    llm_provider: str = "openai-compatible"  # openai-compatible, anthropic, gemini, ollama
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_timeout_seconds: float = 15.0

    # CORS
    allowed_origins: list[str] = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    def validate_environment(self) -> None:
        if self.environment.lower() == "production" and self.demo_mode:
            raise RuntimeError(
                "Security violation: DEMO_MODE must not be enabled when ENVIRONMENT is production."
            )


settings = Settings()
settings.validate_environment()
