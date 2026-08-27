import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """StudioSonar System Configuration."""
    
    # GCP & Project Settings
    gcp_project_id: str = Field(default="studiosonar-dev", env="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", env="GCP_LOCATION")
    bigquery_dataset: str = Field(default="studiosonar_analytics", env="BIGQUERY_DATASET")
    
    # Gemini AI & YouTube API
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.7-flash", env="GEMINI_MODEL")
    youtube_data_api_key: str = Field(default="", env="YOUTUBE_DATA_API_KEY")
    
    # Execution Mode: Default is 100% "live" for production APIs & BigQuery
    execution_mode: Literal["live", "mock"] = Field(default="live", env="EXECUTION_MODE")

    
    # Distributed Google ADK A2A Microservice URLs
    channel_monitor_url: str = Field(default="", env="CHANNEL_MONITOR_URL")
    anomaly_detector_url: str = Field(default="", env="ANOMALY_DETECTOR_URL")
    pr_strategist_url: str = Field(default="", env="PR_STRATEGIST_URL")
    content_creator_url: str = Field(default="", env="CONTENT_CREATOR_URL")

    # Integrations
    slack_webhook_url: str = Field(default="", env="SLACK_WEBHOOK_URL")

    notion_api_key: str = Field(default="", env="NOTION_API_KEY")
    notion_database_id: str = Field(default="", env="NOTION_DATABASE_ID")
    google_drive_folder_id: str = Field(default="", env="GOOGLE_DRIVE_FOLDER_ID")
    
    # Guardrails & Anomaly Thresholds
    min_anomaly_velocity_pct: float = Field(default=250.0, env="MIN_ANOMALY_VELOCITY_PCT")
    critical_sentiment_threshold: float = Field(default=-0.60, env="CRITICAL_SENTIMENT_THRESHOLD")
    confidence_threshold: float = Field(default=0.85, env="CONFIDENCE_THRESHOLD")
    
    # Server
    port: int = Field(default=8080, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
