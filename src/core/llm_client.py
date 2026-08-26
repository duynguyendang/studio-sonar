import os
import logging
from typing import Optional
from src.core.config import settings

logger = logging.getLogger("studiosonar.llm")

class GeminiLLMClient:
    """
    Unified Google Gemini LLM Client for Google ADK Multi-Agent System.
    Supports both Google AI Studio API Keys and Google Cloud Vertex AI ADC.
    """

    def __init__(self):
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_location
        self.model_name = settings.gemini_model or "gemini-2.5-flash"
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            # 1. Primary: Google AI Studio Key (Direct Fast Gateway)
            if self.api_key and "mock" not in self.api_key.lower():
                try:
                    self._client = genai.Client(api_key=self.api_key)
                    logger.info(f"Initialized Gemini Client via Google AI API Key (Model: {self.model_name})")
                    return
                except Exception as e:
                    logger.warning(f"Google AI API key init notice: {e}")

            # 2. Secondary: Google Cloud Vertex AI ADC (Zero-Key on Cloud Run)
            if self.project_id:
                try:
                    self._client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
                    logger.info(f"Initialized Gemini Client via Vertex AI Zero-Key (Project: {self.project_id}, Region: {self.location})")
                    return
                except Exception as e:
                    logger.warning(f"Vertex AI initialization notice: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize google.genai Client: {e}")

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """Generates dynamic completion using Google Gemini Flash on Vertex AI / Google AI Studio."""
        if not self._client:
            self._init_client()

        if self._client:
            models_to_try = [self.model_name, "gemini-2.5-flash", "gemini-1.5-flash"]
            for m in models_to_try:
                try:
                    from google.genai import types
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                        max_output_tokens=1024
                    ) if system_instruction else types.GenerateContentConfig(temperature=0.3)
                    
                    res = self._client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=config
                    )
                    if res and res.text:
                        return res.text.strip()
                except Exception as e:
                    logger.debug(f"Model {m} attempt notice: {e}")

        return None

llm_client = GeminiLLMClient()
