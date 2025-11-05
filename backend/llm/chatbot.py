"""
Chatbot for Concya Voice AI Backend
Based on Unmute's chatbot implementation
"""
from logging import getLogger
from typing import Any, Literal

try:
    from .llm_utils import preprocess_messages_for_llm
    from .system_prompt import ConstantInstructions, Instructions
except ImportError:
    from llm_utils import preprocess_messages_for_llm
    from system_prompt import ConstantInstructions, Instructions

ConversationState = Literal["waiting_for_user", "user_speaking", "bot_speaking"]

logger = getLogger(__name__)


class Chatbot:
    """Manages conversation state and LLM interactions"""

    def __init__(self):
        # Chat history as OpenAI message format
        self.chat_history: list[dict[Any, Any]] = [
            {"role": "system", "content": ConstantInstructions().make_system_prompt()}
        ]
        self._instructions: Instructions | None = None

    def conversation_state(self) -> ConversationState:
        """Get current conversation state based on chat history"""
        if not self.chat_history:
            return "waiting_for_user"

        last_message = self.chat_history[-1]
        if last_message["role"] == "assistant":
            return "bot_speaking"
        elif last_message["role"] == "user":
            if last_message["content"].strip() != "":
                return "user_speaking"
            else:
                return "waiting_for_user"
        elif last_message["role"] == "system":
            return "waiting_for_user"
        else:
            raise RuntimeError(f"Unknown role: {last_message['role']}")

    async def add_chat_message_delta(
        self,
        delta: str,
        role: Literal["user", "assistant"],
        generating_message_i: int | None = None,  # Avoid race conditions
    ) -> bool:
        """
        Add a partial message to the chat history, adding spaces if necessary.

        Returns:
            True if the message is a new message, False if it is a continuation of
            the last message.
        """
        # Handle special interruption character
        if delta == "\x00":  # INTERRUPTION_CHAR
            # Truncate the last assistant message
            for i in range(len(self.chat_history) - 1, -1, -1):
                if self.chat_history[i]["role"] == "assistant":
                    self.chat_history[i]["content"] = self.chat_history[i]["content"].rstrip()
                    break
            return False

        # Handle user silence marker
        if delta == "[USER_SILENCE]":
            # Add empty user message to indicate silence
            self.chat_history.append({"role": "user", "content": ""})
            return True

        # Find the last message with this role
        last_message_i = None
        for i in range(len(self.chat_history) - 1, -1, -1):
            if self.chat_history[i]["role"] == role:
                last_message_i = i
                break

        if last_message_i is None:
            # This is the first message with this role
            self.chat_history.append({"role": role, "content": delta})
            return True
        else:
            # This is a continuation of an existing message
            self.chat_history[last_message_i]["content"] += delta
            return False

    def get_instructions(self) -> Instructions | None:
        """Get current instructions"""
        return self._instructions

    def set_instructions(self, instructions: Instructions):
        """Set new instructions and update system prompt"""
        self._instructions = instructions
        # Update system message
        for i, msg in enumerate(self.chat_history):
            if msg["role"] == "system":
                self.chat_history[i]["content"] = instructions.make_system_prompt()
                break

    def preprocess_messages(self) -> list[dict[str, Any]]:
        """Preprocess messages for LLM consumption"""
        return preprocess_messages_for_llm(self.chat_history)

    def clear_history(self):
        """Clear chat history except system message"""
        system_msg = None
        for msg in self.chat_history:
            if msg["role"] == "system":
                system_msg = msg
                break

        self.chat_history = [system_msg] if system_msg else []

    def get_recent_messages(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent messages from chat history"""
        return self.chat_history[-limit:] if len(self.chat_history) > limit else self.chat_history


# Test the chatbot
async def test_chatbot():
    """Test chatbot functionality"""
    chatbot = Chatbot()

    print(f"Initial state: {chatbot.conversation_state()}")

    # Add user message
    is_new = await chatbot.add_chat_message_delta("Hello", "user")
    print(f"Added 'Hello' - New message: {is_new}")
    print(f"State after user message: {chatbot.conversation_state()}")

    # Add assistant response
    is_new = await chatbot.add_chat_message_delta("Hi there!", "assistant")
    print(f"Added 'Hi there!' - New message: {is_new}")
    print(f"State after assistant message: {chatbot.conversation_state()}")

    # Continue assistant message
    is_new = await chatbot.add_chat_message_delta(" How can I help you?", "assistant")
    print(f"Continued assistant message - New message: {is_new}")

    print(f"Final state: {chatbot.conversation_state()}")
    print("Chat history:")
    for i, msg in enumerate(chatbot.chat_history):
        print(f"  {i}: {msg['role']}: {msg['content']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chatbot())
