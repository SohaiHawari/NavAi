"""
NavAI - AI Question & Answer Engine
Generates natural language answers using LLM (OpenAI or Groq).
"""

import json
import logging
from typing import Optional

logger = logging.getLogger("NavAI.QnA")

# System prompt for the LLM
SYSTEM_PROMPT = """You are NavAI, a friendly and helpful AI assistant designed to help visually impaired users understand their surroundings.

Your role:
- Describe the user's environment clearly and concisely
- Answer questions about what is around them
- Read out any text visible in their surroundings
- Warn about potential obstacles or hazards
- Be warm, supportive, and reassuring

Rules:
1. Keep responses SHORT (1-3 sentences max)
2. Use simple, clear language
3. Mention spatial positions (left, right, in front, behind) when available
4. Prioritize safety information (obstacles, stairs, vehicles)
5. If you detect text (like signs), always mention it
6. If context is empty or unclear, say so honestly
7. Never make up objects that aren't in the context
8. Use natural, conversational tone as if speaking to a friend

Example:
Context: {"objects": [{"label": "person", "position": "center"}, {"label": "chair", "position": "right"}], "texts": [{"text": "EXIT"}]}
Question: "What is in front of me?"
Answer: "A person is standing in front of you, and there's a chair to your right. I can also see an exit sign nearby."
"""


class QnAEngine:
    """
    AI-powered Question & Answer engine using LLM APIs.

    Supports OpenAI (GPT-4o-mini) and Groq (LLaMA 3.1) as providers.
    Takes a user question + visual context and generates a natural answer.
    """

    def __init__(self, provider: str = "groq", api_key: str = "", model: str = ""):
        """
        Initialize the QnA engine.

        Args:
            provider: "openai" or "groq"
            api_key: API key for the chosen provider
            model: Model name to use
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.client = None

        # Track conversation history for context memory
        self.history: list = []
        self.max_history = 5  # Keep last 5 interactions

        self._initialize_client()

    def _initialize_client(self):
        """Initialize the LLM client based on provider."""
        try:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model: {self.model}")

            elif self.provider == "groq":
                from groq import AsyncGroq
                self.client = AsyncGroq(api_key=self.api_key)
                logger.info(f"Groq client initialized with model: {self.model}")

            else:
                raise ValueError(f"Unknown provider: {self.provider}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None

    async def generate_answer(
        self,
        question: str,
        context: str,
        include_history: bool = True,
    ) -> str:
        """
        Generate a natural language answer.

        Args:
            question: User's question (from STT)
            context: JSON string of visual context (objects + text)
            include_history: Whether to include conversation history

        Returns:
            Natural language answer string
        """
        if self.client is None:
            return self._fallback_answer(question, context)

        try:
            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add conversation history for context memory
            if include_history and self.history:
                for h in self.history[-self.max_history:]:
                    messages.append({"role": "user", "content": h["user"]})
                    messages.append({"role": "assistant", "content": h["assistant"]})

            # Current query
            user_message = (
                f"Visual Context: {context}\n\n"
                f"User Question: {question}\n\n"
                f"Please provide a helpful, concise answer."
            )
            messages.append({"role": "user", "content": user_message})

            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )

            answer = response.choices[0].message.content.strip()

            # Store in history for memory feature
            self.history.append({
                "user": user_message,
                "assistant": answer,
            })

            logger.info(f"Generated answer: {answer[:100]}...")
            return answer

        except Exception as e:
            error_msg = str(e).lower()
            if "model" in error_msg and ("not found" in error_msg or "deactivated" in error_msg):
                logger.error(f"LLM model unavailable ({self.model}): {e}")
            else:
                logger.error(f"LLM generation failed: {e}")
            return self._fallback_answer(question, context)

    def _fallback_answer(self, question: str, context: str) -> str:
        """
        Generate a basic answer without LLM (rule-based fallback).

        Used when LLM is unavailable or fails.

        Args:
            question: User's question
            context: Context JSON string

        Returns:
            Basic descriptive answer
        """
        try:
            if context is None:
                return "I'm having trouble processing the image right now. Please try again."
            ctx = json.loads(context) if isinstance(context, str) else context
            if ctx is None:
                return "I'm having trouble processing the image right now. Please try again."
        except (json.JSONDecodeError, TypeError):
            return "I'm having trouble processing the image right now. Please try again."

        parts = []

        # Describe objects
        objects = ctx.get("objects", [])
        if objects:
            obj_descriptions = []
            for obj in objects[:5]:  # Limit to top 5
                label = obj.get("label", "object")
                position = obj.get("position", "nearby")
                pos_text = {
                    "left": "to your left",
                    "center": "in front of you",
                    "right": "to your right",
                }.get(position, "nearby")
                obj_descriptions.append(f"a {label} {pos_text}")

            if obj_descriptions:
                parts.append("I can see " + ", ".join(obj_descriptions))

        # Describe text
        texts = ctx.get("texts", [])
        if texts:
            text_content = ", ".join(t.get("text", "") for t in texts if t.get("text"))
            if text_content:
                parts.append(f'I can read the text: "{text_content}"')

        if parts:
            return ". ".join(parts) + "."
        else:
            return "I don't see anything notable in the current view. Try pointing the camera in a different direction."

    def clear_history(self):
        """Clear conversation history."""
        self.history = []
        logger.info("Conversation history cleared")
