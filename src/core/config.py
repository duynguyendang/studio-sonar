from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """StudioSonar System Configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True
    )

    # GCP & Project Settings
    gcp_project_id: str = Field(default="studiosonar-dev", validation_alias="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", validation_alias="GCP_LOCATION")
    bigquery_dataset: str = Field(default="studiosonar_analytics", validation_alias="BIGQUERY_DATASET")
    
    # Gemini AI & YouTube API
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.8-flash", validation_alias="GEMINI_MODEL")
    youtube_data_api_key: str = Field(default="", validation_alias="YOUTUBE_DATA_API_KEY")
    
    # Hot Path Real-Time Analytics: ClickHouse
    clickhouse_host: str = Field(default="localhost", validation_alias="CLICKHOUSE_HOST")
    clickhouse_port: int = Field(default=8123, validation_alias="CLICKHOUSE_PORT")
    clickhouse_user: str = Field(default="default", validation_alias="CLICKHOUSE_USER")
    clickhouse_password: str = Field(default="", validation_alias="CLICKHOUSE_PASSWORD")
    clickhouse_database: str = Field(default="studiosonar", validation_alias="CLICKHOUSE_DATABASE")
    clickhouse_secure: bool = Field(default=False, validation_alias="CLICKHOUSE_SECURE")

    # Autonomous External Grounding: Google Search API / CSE / Vertex AI Grounding
    google_search_api_key: str = Field(default="", validation_alias="GOOGLE_SEARCH_API_KEY")
    google_search_cse_id: str = Field(default="", validation_alias="GOOGLE_SEARCH_CSE_ID")
    google_search_enabled: bool = Field(default=True, validation_alias="GOOGLE_SEARCH_ENABLED")
    use_vertex_search_grounding: bool = Field(default=True, validation_alias="USE_VERTEX_SEARCH_GROUNDING")

    # Execution Mode: Default is 100% "live" for production APIs & BigQuery
    execution_mode: Literal["live", "mock"] = Field(default="live", validation_alias="EXECUTION_MODE")

    # Distributed Google ADK A2A Microservice URLs
    channel_monitor_url: str = Field(default="", validation_alias="CHANNEL_MONITOR_URL")
    anomaly_detector_url: str = Field(default="", validation_alias="ANOMALY_DETECTOR_URL")
    pr_strategist_url: str = Field(default="", validation_alias="PR_STRATEGIST_URL")
    content_creator_url: str = Field(default="", validation_alias="CONTENT_CREATOR_URL")

    # Integrations
    slack_webhook_url: str = Field(default="", validation_alias="SLACK_WEBHOOK_URL")

    notion_api_key: str = Field(default="", validation_alias="NOTION_API_KEY")
    notion_database_id: str = Field(default="", validation_alias="NOTION_DATABASE_ID")
    google_drive_folder_id: str = Field(default="", validation_alias="GOOGLE_DRIVE_FOLDER_ID")
    
    # Guardrails & Anomaly Thresholds
    min_anomaly_velocity_pct: float = Field(default=250.0, validation_alias="MIN_ANOMALY_VELOCITY_PCT")
    critical_sentiment_threshold: float = Field(default=-0.60, validation_alias="CRITICAL_SENTIMENT_THRESHOLD")
    confidence_threshold: float = Field(default=0.85, validation_alias="CONFIDENCE_THRESHOLD")
    
    # Server
    port: int = Field(default=8080, validation_alias="PORT")
    host: str = Field(default="0.0.0.0", validation_alias="HOST")

settings = Settings()
