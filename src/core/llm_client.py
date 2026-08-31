import os
import time
import logging
import threading
from typing import Optional
from src.core.config import settings

logger = logging.getLogger("studiosonar.llm")

AGENT_PLATFORM_OPENAPI_PATH = (
    "https://aiplatform.googleapis.com/v1/projects/{project_id}"
    "/locations/global/endpoints/openapi/chat/completions"
)

class GeminiLLMClient:
    """
    Unified Google Gemini LLM Client for the Google ADK Multi-Agent System.

    STRICT single-model policy: every call targets ONE model (gemini-3.7-flash).
    There is no cross-model fallback. Transport resolution:
      1. Gemini Enterprise Agent Platform (OpenAI-compatible global endpoint) via
         Application Default Credentials - this is how gemini-3.x is served.
      2. google-genai SDK (API-key gateway) - same model only.
    """

    MAX_RETRIES = 4
    BACKOFF_BASE = 1.5  # seconds; grows exponentially per attempt

    def __init__(self):
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_location
        self.model_name = settings.gemini_model or "gemini-3.7-flash"
        self._client = None
        self._credentials = None
        self._agent_platform_ready = False
        self._token_lock = threading.RLock()
        self._init_agent_platform()
        self._init_client()

    def _sleep_backoff(self, attempt: int) -> None:
        # Exponential backoff to ride out transient 429/5xx without switching model.
        time.sleep(min(self.BACKOFF_BASE * (2 ** attempt), 20))

    # ------------------------------------------------------------------ agent platform
    def _init_agent_platform(self):
        """Prepares ADC credentials for the Gemini Enterprise Agent Platform global endpoint."""
        try:
            from google.auth import default as google_auth_default
            credentials, project = google_auth_default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self._credentials = credentials
            if project:
                self.project_id = project
            self._agent_platform_ready = True
            logger.info("Initialized Gemini Client via Agent Platform ADC (identity: %s)", self.project_id)
        except Exception as e:
            logger.debug(f"Agent Platform ADC init notice: {e}")

    def _get_agent_token(self) -> Optional[str]:
        # google-auth credentials are not safe for concurrent refresh from the
        # parallel report-authoring thread pool; serialize with a lock.
        with self._token_lock:
            try:
                from google.auth.transport.requests import Request
                if not self._credentials.valid:
                    self._credentials.refresh(Request())
                return self._credentials.token
            except Exception as e:
                logger.debug(f"Agent Platform token refresh notice: {e}")
                return None

    def _generate_agent_platform(self, prompt: str, system_instruction: Optional[str], model: str) -> Optional[str]:
        token = self._get_agent_token()
        if not token:
            return None
        import requests
        url = AGENT_PLATFORM_OPENAPI_PATH.format(project_id=self.project_id)
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": f"google/{model}",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048,
        }
        try:
            res = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            if res.status_code == 200:
                data = res.json()
                content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
                if content:
                    logger.info(f"Agent Platform OK -> {model} ({len(content)} chars)")
                    return content.strip()
                logger.debug(f"Agent Platform model {model}: empty content")
                return None
            logger.info(f"Agent Platform model {model}: HTTP {res.status_code} {res.text[:140]}")
        except Exception as e:
            logger.debug(f"Agent Platform model {model} request notice: {e}")
        return None

    # ------------------------------------------------------------------ google-genai
    def _init_client(self):
        try:
            from google import genai
            # 1. Google AI Studio / Gemini Developer API Key (Fast Gateway)
            if self.api_key and "mock" not in self.api_key.lower():
                try:
                    self._client = genai.Client(api_key=self.api_key)
                    logger.info(f"Initialized Gemini Client via Google AI API Key (Model: {self.model_name})")
                    return
                except Exception as e:
                    logger.warning(f"Google AI API key init notice: {e}")

            # 2. Google Cloud Vertex AI ADC (per-region, Zero-Key on Cloud Run)
            if self.project_id and os.getenv("K_SERVICE"):  # Only on Cloud Run environment
                try:
                    self._client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
                    logger.info(f"Initialized Gemini Client via Vertex AI Zero-Key (Project: {self.project_id}, Region: {self.location})")
                    return
                except Exception as e:
                    logger.warning(f"Vertex AI initialization notice: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize google.genai Client: {e}")

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """
        Generate a completion. STRICTLY uses the configured model (gemini-3.7-flash)
        for every call so outputs stay consistent — it NEVER falls back to another
        model. Transient failures (429/5xx/empty) are retried on the SAME model with
        exponential backoff; if all retries fail we return None and let the caller
        use its deterministic fallback rather than a different model.

        Transport policy:
          - On Cloud Run the Gemini Enterprise Agent Platform (global endpoint via
            ADC) is the authoritative transport and is the ONLY one that serves
            gemini-3.x. If it is available we use it exclusively and NEVER fall
            through to the per-region Vertex :generateContent path (which returns
            404 for 3.x and only wastes calls/time).
          - The google-genai client is used solely when Agent Platform is NOT
            available (e.g. local dev with a valid generativelanguage API key).
        """
        model = self.model_name or "gemini-3.7-flash"

        # Authoritative transport: Agent Platform global OpenAI-compatible endpoint.
        if self._agent_platform_ready:
            for attempt in range(self.MAX_RETRIES):
                text = self._generate_agent_platform(prompt, system_instruction, model)
                if text:
                    return text
                self._sleep_backoff(attempt)
            logger.warning(f"generate() exhausted all Agent Platform retries for {model}")
            return None

        # Fallback transport (only when Agent Platform is unavailable): google-genai SDK.
        if not self._client:
            self._init_client()
        if self._client:
            for attempt in range(self.MAX_RETRIES):
                try:
                    from google.genai import types
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                        max_output_tokens=2048,
                    ) if system_instruction else types.GenerateContentConfig(
                        temperature=0.3, max_output_tokens=2048
                    )
                    res = self._client.models.generate_content(
                        model=model, contents=prompt, config=config
                    )
                    if res and res.text:
                        return res.text.strip()
                    logger.debug(f"Model {model} attempt {attempt}: empty response")
                except Exception as e:
                    logger.debug(f"Model {model} attempt {attempt} notice: {e}")
                self._sleep_backoff(attempt)

        logger.warning(f"generate() exhausted all retries for model {model} (no cross-model fallback)")
        return None

llm_client = GeminiLLMClient()