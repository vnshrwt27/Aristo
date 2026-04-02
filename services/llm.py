import os
import json
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self, provider: str | None = None, model: str | None = None, temperature: float = 0):
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq").lower()
        self.model = model or self._default_model()
        self.temperature = temperature
        self._client = None

    def _default_model(self) -> str:
        return {
            "groq": "llama-3.3-70b-versatile",
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "google": "gemini-2.0-flash",
        }.get(self.provider, "llama-3.3-70b-versatile")

    def _get_client(self):
        if self._client is not None:
            return self._client

        if self.provider == "groq":
            from langchain_groq import ChatGroq
            self._client = ChatGroq(
                model=self.model,
                temperature=self.temperature,
                api_key=os.getenv("GROQ_API_KEY"),
            )
        elif self.provider == "openai":
            from langchain_openai import ChatOpenAI
            self._client = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self._client = ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        elif self.provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            self._client = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        return self._client

    def invoke(self, system: str, human: str) -> str:
        client = self._get_client()
        resp = client.invoke([("system", system), ("human", human)])
        return resp.content

    def invoke_json(self, system: str, human: str) -> dict:
        prompt = system + "\n\nReturn ONLY valid JSON, no markdown or extra text."
        content = self.invoke(prompt, human).strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        return json.loads(content)
