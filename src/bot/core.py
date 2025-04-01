import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BookingPreferences(BaseModel):
    event_id: str
    preferred_rows: List[str]
    preferred_seats: List[str]
    max_price: float
    quantity: int

class TicketInfo(BaseModel):
    event_id: str
    row: str
    seat: str
    price: float
    status: str
    hold_token: Optional[str] = None

class WeBookBot:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://webook.com"  # Replace with actual WeBook URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def initialize(self):
        """Initialize the bot with a new session."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        """Close the bot's session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def search_events(self, query: str) -> List[Dict]:
        """Search for events matching the query."""
        try:
            async with self.session.get(f"{self.base_url}/search?q={query}") as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_events(html)
                else:
                    logger.error(f"Failed to search events: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error searching events: {str(e)}")
            return []

    async def get_available_seats(self, event_id: str) -> List[TicketInfo]:
        """Get available seats for a specific event."""
        try:
            async with self.session.get(f"{self.base_url}/events/{event_id}/seats") as response:
                if response.status == 200:
                    data = await response.json()
                    return [TicketInfo(**seat) for seat in data.get("seats", [])]
                else:
                    logger.error(f"Failed to get seats: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting seats: {str(e)}")
            return []

    async def hold_tickets(self, event_id: str, seats: List[TicketInfo]) -> bool:
        """Hold selected tickets for a short period."""
        try:
            payload = {
                "event_id": event_id,
                "seats": [{"row": seat.row, "seat": seat.seat} for seat in seats]
            }
            async with self.session.post(f"{self.base_url}/hold", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("success", False)
                return False
        except Exception as e:
            logger.error(f"Error holding tickets: {str(e)}")
            return False

    async def book_tickets(self, event_id: str, seats: List[TicketInfo]) -> bool:
        """Book the held tickets."""
        try:
            payload = {
                "event_id": event_id,
                "seats": [{"row": seat.row, "seat": seat.seat} for seat in seats]
            }
            async with self.session.post(f"{self.base_url}/book", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("success", False)
                return False
        except Exception as e:
            logger.error(f"Error booking tickets: {str(e)}")
            return False

    def _parse_events(self, html: str) -> List[Dict]:
        """Parse event data from HTML response."""
        events = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            # Add parsing logic based on WeBook's HTML structure
            # This is a placeholder - actual implementation will depend on the website structure
            return events
        except Exception as e:
            logger.error(f"Error parsing events: {str(e)}")
            return events

    async def find_and_book_tickets(self, preferences: BookingPreferences) -> bool:
        """Main method to find and book tickets based on preferences."""
        try:
            # Get available seats
            available_seats = await self.get_available_seats(preferences.event_id)
            
            # Filter seats based on preferences
            matching_seats = [
                seat for seat in available_seats
                if seat.row in preferences.preferred_rows
                and seat.seat in preferences.preferred_seats
                and seat.price <= preferences.max_price
                and seat.status == "available"
            ]

            if len(matching_seats) < preferences.quantity:
                logger.warning(f"Not enough matching seats found. Found {len(matching_seats)}, needed {preferences.quantity}")
                return False

            # Take only the required quantity
            selected_seats = matching_seats[:preferences.quantity]

            # Hold the tickets
            if not await self.hold_tickets(preferences.event_id, selected_seats):
                logger.error("Failed to hold tickets")
                return False

            # Book the tickets
            if not await self.book_tickets(preferences.event_id, selected_seats):
                logger.error("Failed to book tickets")
                return False

            logger.info(f"Successfully booked {len(selected_seats)} tickets")
            return True

        except Exception as e:
            logger.error(f"Error in find_and_book_tickets: {str(e)}")
            return False 