import pytest
import asyncio
from src.bot.core import WeBookBot, BookingPreferences, TicketInfo

@pytest.fixture
async def bot():
    """Create a bot instance for testing."""
    bot = WeBookBot()
    await bot.initialize()
    yield bot
    await bot.close()

@pytest.mark.asyncio
async def test_search_events(bot):
    """Test event search functionality."""
    events = await bot.search_events("test event")
    assert isinstance(events, list)

@pytest.mark.asyncio
async def test_get_available_seats(bot):
    """Test getting available seats."""
    seats = await bot.get_available_seats("test_event_id")
    assert isinstance(seats, list)
    for seat in seats:
        assert isinstance(seat, TicketInfo)

@pytest.mark.asyncio
async def test_hold_tickets(bot):
    """Test ticket holding functionality."""
    seats = [
        TicketInfo(
            event_id="test_event_id",
            row="A",
            seat="1",
            price=100.0,
            status="available"
        )
    ]
    success = await bot.hold_tickets("test_event_id", seats)
    assert isinstance(success, bool)

@pytest.mark.asyncio
async def test_book_tickets(bot):
    """Test ticket booking functionality."""
    seats = [
        TicketInfo(
            event_id="test_event_id",
            row="A",
            seat="1",
            price=100.0,
            status="available"
        )
    ]
    success = await bot.book_tickets("test_event_id", seats)
    assert isinstance(success, bool)

@pytest.mark.asyncio
async def test_find_and_book_tickets(bot):
    """Test the complete booking process."""
    preferences = BookingPreferences(
        event_id="test_event_id",
        preferred_rows=["A", "B"],
        preferred_seats=["1", "2"],
        max_price=200.0,
        quantity=2
    )
    success = await bot.find_and_book_tickets(preferences)
    assert isinstance(success, bool) 