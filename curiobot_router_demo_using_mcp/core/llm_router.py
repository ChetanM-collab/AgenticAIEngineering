import os
import json
from typing import Any, Dict, List, Optional, Literal

from utils.logging_utils import LoggerFactory
from core.openai_config import make_openai_client, DEFAULT_MODEL
from core.routing_types import RouterPlan

log = LoggerFactory.get_logger("curiobot.router")

Provider = Literal["openai"]


class LLMRouter:
    """Simple LLM-based router that chooses one of the supported tools.

    It always returns a dict compatible with RouterPlan:
      {
        "tool": "get_news" | "get_weather" | "get_wiki" | "direct_answer" | "none",
        "args": { ... },
        "reason": "why this tool"
      }
    """

    def __init__(self, provider: Optional[Provider] = None) -> None:
        self.provider: Provider = (provider or os.getenv("MODEL_PROVIDER", "openai")).lower()  # type: ignore[assignment]
        log.info("LLMRouter init: provider=%s", self.provider)
        self._init_client(self.provider)

    def _init_client(self, provider: str) -> None:
        if provider == "openai":
            log.info("LLMRouter: initializing OpenAI client")
            self.client = make_openai_client()
            self.model: str = DEFAULT_MODEL
        else:
            raise ValueError(f"Invalid provider: {provider}")

    def route(
        self,
        question: str,
        provider: Optional[str] = None,
        max_depth: int = 1,
    ) -> Dict[str, Any]:
        """Decide which tool to call for a given question.

        Returns a dict of the form:
          {
            "tool": "get_news" | "get_weather" | "get_wiki" | "direct_answer" | "none",
            "args": { ... },
            "reason": "string"
          }
        """

        # Allow temporarily overriding provider
        if provider:
            provider = provider.lower()
            if provider != self.provider:
                self.provider = provider  # type: ignore[assignment]
                self._init_client(self.provider)

        log.info("LLMRouter.route called for question=%s", question)
        log.info("LLMRouter.provider=%s", self.provider)

        tools: List[str] = ["get_wiki", "get_news", "get_weather"]

        system_prompt = (
            "You are a helpful router. Decide which tool to call based on the user's question. "
            f"Available tools: {', '.join(tools)}. "
            f"You may call tools up to {max_depth} times (though you normally only need one decision). "
            "Return ONLY strict JSON on one line using this schema: "
            "{\"tool\": \"string\", \"args\": {}, \"reason\": \"string\"}. "
            "If no tool fits and the LLM should answer directly, use: "
            "{\"tool\": \"direct_answer\", \"args\": {\"answer\": \"...\"}, \"reason\": \"...\"}."
        )

        user_prompt = (
            "Question: {question}\n"
            "Return only the JSON object, no other text."
        ).format(question=question)

        if self.provider == "openai":
            from openai import OpenAI  # imported here to keep core/openai_config minimal
            log.info("LLMRouter - Calling OpenAI LLM with model=%s", self.model)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            log.debug("LLMRouter raw content: %s", content)

            try:
                raw = json.loads(content or "{}")
                plan = RouterPlan.model_validate(raw)
                normalised = plan.model_dump()
                log.info("LLMRouter plan=%s", normalised)
                return normalised
            except Exception as e:
                log.exception("LLMRouter failed to parse JSON plan; falling back. content=%r", content)
                # Fallback: treat the content as a direct answer
                fallback = RouterPlan(
                    tool="direct_answer",
                    args={"answer": content or "I could not decide which tool to use."},
                    reason=f"fallback due to parse error: {e}",
                )
                return fallback.model_dump()

        raise RuntimeError(f"Unsupported provider in route(): {self.provider}")
