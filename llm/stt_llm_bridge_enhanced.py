"""
Enhanced STT to LLM Bridge with Intent Parsing and Structured Data Capture
Concya Restaurant Voice Agent
"""

import argparse
import asyncio
import json
import subprocess
import signal
import os
from openai_connector import OpenAIConnector
from intent_parser import IntentParser


class ReservationAgent:
    """Manages the reservation conversation flow."""
    
    def __init__(self, llm_connector: OpenAIConnector):
        self.llm = llm_connector
        self.parser = IntentParser()
        self.conversation_state = "greeting"  # greeting, collecting, confirming, complete
        self.confirmation_pending = False
        
    def process_user_input(self, user_text: str) -> str:
        """
        Process user input and return appropriate response.
        
        States:
        - greeting: Initial greeting
        - collecting: Gathering reservation details
        - confirming: User reviewing details before booking
        - complete: Reservation confirmed
        """
        # Parse the input
        parsed = self.parser.parse(user_text)
        
        print(f"   📊 Intent: {parsed['intent']}")
        if parsed['entities']:
            print(f"   📦 Extracted: {parsed['entities']}")
        
        # Handle different conversation states
        if self.conversation_state == "greeting":
            return self._handle_greeting(parsed)
        
        elif self.conversation_state == "collecting":
            return self._handle_collecting(parsed)
        
        elif self.conversation_state == "confirming":
            return self._handle_confirming(parsed, user_text)
        
        elif self.conversation_state == "complete":
            return "Your reservation is already complete! Would you like to make another reservation?"
        
        return "I'm not sure how to help with that. Let's continue with your reservation."
    
    def _handle_greeting(self, parsed: dict) -> str:
        """Handle initial greeting state."""
        if parsed['intent'] == 'make_reservation' or any(parsed['entities']):
            self.conversation_state = "collecting"
            return self._handle_collecting(parsed)
        
        self.conversation_state = "collecting"
        return "Welcome to Concya! I'd be happy to help you make a reservation. How many people will be dining?"
    
    def _handle_collecting(self, parsed: dict) -> str:
        """Handle data collection state."""
        # Check if reservation is complete
        if parsed['is_complete']:
            self.conversation_state = "confirming"
            return self._generate_confirmation()
        
        # Ask for next missing field
        next_question = self.parser.get_next_question()
        
        if next_question == "confirm":
            self.conversation_state = "confirming"
            return self._generate_confirmation()
        
        # Acknowledge what we got and ask for next
        response = ""
        if parsed['entities']:
            # Acknowledge the information received
            if 'party_size' in parsed['entities']:
                response = f"Great! A table for {parsed['entities']['party_size']}. "
            elif 'date' in parsed['entities']:
                date_obj = self.parser.reservation._format_date(parsed['entities']['date'])
                response = f"Perfect, {date_obj}. "
            elif 'time' in parsed['entities']:
                time_obj = self.parser.reservation._format_time(parsed['entities']['time'])
                response = f"Excellent, {time_obj}. "
            elif 'name' in parsed['entities']:
                response = f"Thank you, {parsed['entities']['name']}. "
        
        response += next_question
        return response
    
    def _handle_confirming(self, parsed: dict, user_text: str) -> str:
        """Handle confirmation state."""
        text_lower = user_text.lower()
        
        # Check for confirmation
        if any(word in text_lower for word in ['yes', 'correct', 'right', 'confirm', 'yep', 'yeah', 'sure']):
            self.conversation_state = "complete"
            return self._finalize_reservation()
        
        # Check for denial/correction
        if any(word in text_lower for word in ['no', 'wrong', 'incorrect', 'change']):
            self.conversation_state = "collecting"
            self.parser.reset()
            return "I apologize for the confusion. Let's start over. How many people will be dining?"
        
        # If they provide more info instead of yes/no, update and re-confirm
        if parsed['entities']:
            self.conversation_state = "collecting"
            return self._handle_collecting(parsed)
        
        # Ask for confirmation again
        return "I didn't catch that. Could you please confirm if these details are correct? (Yes or No)"
    
    def _generate_confirmation(self) -> str:
        """Generate confirmation message."""
        details = self.parser.reservation.to_natural_language()
        return f"Let me confirm your reservation: {details}. Is this correct?"
    
    def _finalize_reservation(self) -> str:
        """Finalize and confirm the reservation."""
        reservation = self.parser.reservation
        
        # In a real system, this would save to database
        confirmation_message = f"""
Perfect! Your reservation is confirmed:

📅 Date: {reservation._format_date(reservation.date)}
🕐 Time: {reservation._format_time(reservation.time)}
👥 Party Size: {reservation.party_size} {'person' if reservation.party_size == 1 else 'people'}
📝 Name: {reservation.name}

We look forward to seeing you at Concya! You will receive a confirmation via SMS shortly.
Is there anything else I can help you with today?
"""
        return confirmation_message.strip()
    
    def get_reservation_summary(self) -> dict:
        """Get current reservation data."""
        return self.parser.reservation.to_dict()


async def main():
    parser = argparse.ArgumentParser(description="Concya Enhanced STT to LLM Bridge")
    parser.add_argument("--stt-url", default="ws://127.0.0.1:8080", help="URL of the STT server")
    parser.add_argument("--openai-key", required=True, help="Your OpenAI API Key")
    parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    parser.add_argument("--mode", default="structured", choices=["structured", "llm"], 
                       help="structured: use intent parser, llm: use pure LLM")
    args = parser.parse_args()

    print("🍽️  Concya Enhanced Voice Agent")
    print("=" * 60)
    print("Mode: Intent-Based Structured Parsing")
    print("Speak naturally to make a reservation...")
    print("Press Ctrl+C to stop\n")

    # Initialize LLM connector (still used for some responses)
    llm_connector = OpenAIConnector(api_key=args.openai_key, model=args.model)
    
    # Initialize reservation agent
    agent = ReservationAgent(llm_connector)

    # Start STT client as a subprocess
    stt_client_path = os.path.join(os.path.dirname(__file__), "..", "stt", "client", "stt_client.py")
    stt_process = subprocess.Popen(
        ["python", stt_client_path, "--url", args.stt_url, "--json"],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def handle_sigint(signum, frame):
        print("\n\n" + "=" * 60)
        print("🛑 Shutting down...")
        
        # Print final reservation summary
        summary = agent.get_reservation_summary()
        if any(summary.values()):
            print("\n📋 Final Reservation Summary:")
            for key, value in summary.items():
                if value:
                    print(f"   {key}: {value}")
        
        stt_process.terminate()
        exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        for line in stt_process.stdout:
            try:
                stt_data = json.loads(line)
                user_text = stt_data.get('text', '').strip()

                if user_text:
                    print(f"\n👤 User: {user_text}")
                    
                    if args.mode == "structured":
                        # Use structured intent parsing
                        response = agent.process_user_input(user_text)
                        print(f"🤖 Assistant: {response}")
                    else:
                        # Use pure LLM mode
                        print("🤖 Assistant: ", end="", flush=True)
                        response_generator = llm_connector.get_chat_response(user_text)
                        for chunk in response_generator:
                            print(chunk, end="", flush=True)
                        print()
                    
                    print("-" * 60)

            except json.JSONDecodeError:
                print(f"⚠️  Error decoding JSON: {line.strip()}")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                
    except Exception as e:
        print(f"❌ Error with STT subprocess: {e}")
    finally:
        stt_process.terminate()


if __name__ == "__main__":
    asyncio.run(main())

