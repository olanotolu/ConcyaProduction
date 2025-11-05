"""
OpenAI LLM Connector for Concya
Manages chat history and LLM interactions
"""

import os
from typing import AsyncIterator, Optional
from openai import AsyncOpenAI


class OpenAIConnector:
    """Manages connection to OpenAI API and chat history."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None
    ):
        """
        Initialize OpenAI connector.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            system_prompt: Initial system prompt for the conversation
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        
        # Initialize chat history with system prompt
        default_prompt = (
            "You are a helpful restaurant reservation assistant for Concya restaurant. "
            "Be concise, friendly, and professional. Help customers book tables, "
            "answer questions about the menu, and provide restaurant information."
        )
        
        self.chat_history = [{
            "role": "system",
            "content": system_prompt or default_prompt
        }]
    
    async def send_user_message(
        self,
        text: str,
        temperature: float = 0.7,
        stream: bool = True
    ) -> AsyncIterator[str]:
        """
        Send user message to LLM and get response.
        
        Args:
            text: User's message text
            temperature: Sampling temperature (0.0-1.0)
            stream: Whether to stream the response
            
        Yields:
            Response text chunks (if streaming)
        """
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": text
        })
        
        if stream:
            # Stream response
            response_text = ""
            stream_response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    response_text += delta
                    yield delta
            
            # Save complete response to history
            self.chat_history.append({
                "role": "assistant",
                "content": response_text
            })
        else:
            # Non-streaming response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                temperature=temperature
            )
            
            response_text = response.choices[0].message.content
            self.chat_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            yield response_text
    
    def get_chat_history(self) -> list[dict]:
        """Get the current chat history."""
        return self.chat_history.copy()
    
    def clear_history(self, keep_system_prompt: bool = True):
        """
        Clear chat history.
        
        Args:
            keep_system_prompt: Whether to keep the system prompt
        """
        if keep_system_prompt and self.chat_history:
            self.chat_history = [self.chat_history[0]]
        else:
            self.chat_history = []
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        if self.chat_history and self.chat_history[0]["role"] == "system":
            self.chat_history[0]["content"] = prompt
        else:
            self.chat_history.insert(0, {"role": "system", "content": prompt})

