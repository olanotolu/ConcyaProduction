"""
Intent Parser for Concya Restaurant Voice Agent
Extracts structured information from natural language
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class ReservationData:
    """Structured reservation information."""
    party_size: Optional[int] = None
    date: Optional[str] = None  # YYYY-MM-DD format
    time: Optional[str] = None  # HH:MM format (24-hour)
    name: Optional[str] = None
    phone: Optional[str] = None
    special_requests: Optional[str] = None
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return all([
            self.party_size,
            self.date,
            self.time,
            self.name
        ])
    
    def missing_fields(self) -> list[str]:
        """Return list of missing required fields."""
        missing = []
        if not self.party_size:
            missing.append("party size")
        if not self.date:
            missing.append("date")
        if not self.time:
            missing.append("time")
        if not self.name:
            missing.append("name")
        return missing
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_natural_language(self) -> str:
        """Convert to natural language for confirmation."""
        parts = []
        if self.party_size:
            parts.append(f"{self.party_size} {'person' if self.party_size == 1 else 'people'}")
        if self.date:
            parts.append(f"on {self._format_date(self.date)}")
        if self.time:
            parts.append(f"at {self._format_time(self.time)}")
        if self.name:
            parts.append(f"under the name {self.name}")
        
        return ", ".join(parts) if parts else "no details yet"
    
    @staticmethod
    def _format_date(date_str: str) -> str:
        """Format date for display."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%A, %B %d, %Y")
        except:
            return date_str
    
    @staticmethod
    def _format_time(time_str: str) -> str:
        """Format time for display."""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.strftime("%I:%M %p")
        except:
            return time_str


class IntentParser:
    """Parse user intents and extract structured data."""
    
    def __init__(self):
        self.reservation = ReservationData()
    
    def parse(self, text: str) -> dict:
        """
        Parse user input and return extracted information.
        
        Returns:
            dict with keys: intent, entities, reservation_data
        """
        text_lower = text.lower()
        
        # Detect intent
        intent = self._detect_intent(text_lower)
        
        # Extract entities
        entities = {}
        
        if party_size := self._extract_party_size(text_lower):
            entities['party_size'] = party_size
            self.reservation.party_size = party_size
        
        if date := self._extract_date(text_lower):
            entities['date'] = date
            self.reservation.date = date
        
        if time := self._extract_time(text_lower):
            entities['time'] = time
            self.reservation.time = time
        
        if name := self._extract_name(text):
            entities['name'] = name
            self.reservation.name = name
        
        if phone := self._extract_phone(text):
            entities['phone'] = phone
            self.reservation.phone = phone
        
        return {
            'intent': intent,
            'entities': entities,
            'reservation_data': self.reservation.to_dict(),
            'is_complete': self.reservation.is_complete(),
            'missing_fields': self.reservation.missing_fields()
        }
    
    def _detect_intent(self, text: str) -> str:
        """Detect user intent."""
        # Reservation intent
        reservation_keywords = [
            'reservation', 'reserve', 'book', 'table',
            'booking', 'appointment', 'spot'
        ]
        if any(kw in text for kw in reservation_keywords):
            return 'make_reservation'
        
        # Inquiry intent
        inquiry_keywords = ['menu', 'price', 'hours', 'location', 'address']
        if any(kw in text for kw in inquiry_keywords):
            return 'inquiry'
        
        # Cancellation intent
        cancel_keywords = ['cancel', 'change', 'modify', 'reschedule']
        if any(kw in text for kw in cancel_keywords):
            return 'cancel_or_modify'
        
        # Greeting
        if any(word in text for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return 'greeting'
        
        return 'unknown'
    
    def _extract_party_size(self, text: str) -> Optional[int]:
        """Extract number of people."""
        # Pattern: "X people", "party of X", "for X", or just standalone numbers
        patterns = [
            r'\b(\d+)\s+(?:people|person|guests?|pax)\b',
            r'\bparty\s+of\s+(\d+)\b',
            r'\bfor\s+(\d+)\b',
            r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:people|person|guests?)\b',
            r'\b(\d+)\b',  # Standalone digits like "4" or "5"
            r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b',  # Standalone words like "three"
        ]
        
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num_str = match.group(1)
                if num_str in number_words:
                    return number_words[num_str]
                try:
                    return int(num_str)
                except:
                    pass
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date in YYYY-MM-DD format."""
        today = datetime.now()
        
        # Today/tonight
        if any(word in text for word in ['today', 'tonight']):
            return today.strftime("%Y-%m-%d")
        
        # Tomorrow
        if 'tomorrow' in text:
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
        
        # Day of week (e.g., "monday", "next friday")
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if day in text:
                # Find next occurrence of this day
                days_ahead = (i - today.weekday()) % 7
                if days_ahead == 0 and 'next' not in text:
                    days_ahead = 7  # Next week
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime("%Y-%m-%d")
        
        # Specific date patterns (MM/DD, MM-DD, Month DD)
        date_patterns = [
            (r'\b(\d{1,2})[/-](\d{1,2})\b', lambda m: f"{today.year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"),
            (r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})', self._parse_month_day)
        ]
        
        for pattern, parser in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return parser(match)
                except:
                    pass
        
        return None
    
    def _parse_month_day(self, match) -> str:
        """Parse month name + day."""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        month_name = match.group(1).lower()
        day = int(match.group(2))
        month = months[month_name]
        year = datetime.now().year
        return f"{year}-{month:02d}-{day:02d}"
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time in HH:MM format (24-hour)."""
        # Pattern: "7 pm", "7:30 pm", "19:00"
        time_patterns = [
            (r'\b(\d{1,2}):(\d{2})\s*(am|pm)\b', True),   # 7:30 pm
            (r'\b(\d{1,2})\s*(am|pm)\b', False),          # 7 pm
            (r'\b(\d{1,2}):(\d{2})\b', True),             # 19:00
        ]
        
        for pattern, has_minutes in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                
                # Extract minutes based on pattern
                if has_minutes:
                    minute = int(match.group(2))
                    period_idx = 3
                else:
                    minute = 0
                    period_idx = 2
                
                # Extract period (am/pm) if present
                period = None
                if len(match.groups()) >= period_idx and match.group(period_idx):
                    period = match.group(period_idx).lower()
                
                # Convert to 24-hour format
                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0
                
                return f"{hour:02d}:{minute:02d}"
        
        return None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract customer name."""
        # Pattern: "my name is X", "under X", "for X" (after reservation context)
        name_patterns = [
            r'(?:my name is|name is|i am|i\'m|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:under|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number."""
        # Pattern: various phone formats
        phone_patterns = [
            r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',
            r'\b\((\d{3})\)\s*(\d{3})[-.\s]?(\d{4})\b',
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                # Normalize phone number
                digits = ''.join(c for c in match.group(0) if c.isdigit())
                if len(digits) == 10:
                    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        return None
    
    def reset(self):
        """Reset reservation data."""
        self.reservation = ReservationData()
    
    def get_next_question(self) -> str:
        """Get the next question to ask based on missing information."""
        missing = self.reservation.missing_fields()
        
        if not missing:
            return "confirm"
        
        field = missing[0]
        
        questions = {
            "party size": "How many people will be dining?",
            "date": "What date would you like to reserve for?",
            "time": "What time would you prefer?",
            "name": "May I have a name for the reservation?"
        }
        
        return questions.get(field, "Could you provide more details?")

