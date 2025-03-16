# llm_manager.py

import openai
import ollama
import streamlit as st

class LLMManager:
    """
    A helper class to either call a local model via Ollama
    or ChatGPT / OpenAI’s GPT-3.5+ based on user's choice.
    """

    def __init__(self, provider="ollama", ollama_config=None, openai_model="gpt-3.5-turbo"):
        """
        provider: 'ollama' or 'openai'
        ollama_config: dict with model, temperature, etc. for Ollama
        openai_model: which OpenAI model to use (e.g. 'gpt-4' or 'gpt-3.5-turbo')
        """
        self.provider = provider
        self.ollama_config = ollama_config or {}
        self.openai_model = openai_model

        # If we have an OpenAI key in st.secrets, set it
        openai.api_key = st.secrets.get("openai_api_key", None)

    def set_provider(self, provider):
        """Change which provider (ollama or openai) we use."""
        self.provider = provider

    def generate(self, prompt):
        """
        Generate text from either local Ollama model or OpenAI’s ChatGPT.
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt)
        else:
            return self._generate_openai(prompt)

    def _generate_ollama(self, prompt):
        """
        Calls a local model via Ollama. Adjust if your Ollama server
        expects different parameters.
        """
        try:
            response = ollama.chat(
                model=self.ollama_config.get("model", "llama2"),
                messages=[{"role": "user", "content": prompt}],
                options=self.ollama_config
            )
            return response.get("message", {}).get("content", "Keine Antwort erhalten.")
        except Exception as e:
            return f"Ollama-Fehler: {e}"

    def _generate_openai(self, prompt):
        """
        Calls OpenAI’s ChatCompletion endpoint for chat-based completion.
        """
        try:
            if not openai.api_key:
                return "Fehler: Kein OpenAI-API-Key gefunden."
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI-Fehler: {e}"
