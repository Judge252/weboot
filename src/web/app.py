from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import uvicorn
from pathlib import Path
import asyncio
from ..bot.core import WeBookBot, BookingPreferences

app = FastAPI(title="WeBook Tickets Bot")

# Mount static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Bot instance
bot = WeBookBot()

class BookingRequest(BaseModel):
    event_id: str
    preferred_rows: List[str]
    preferred_seats: List[str]
    max_price: float
    quantity: int

@app.on_event("startup")
async def startup_event():
    """Initialize the bot when the application starts."""
    await bot.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down."""
    await bot.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "WeBook Tickets Bot"}
    )

@app.post("/api/book")
async def book_tickets(booking_request: BookingRequest):
    """Handle ticket booking requests."""
    try:
        preferences = BookingPreferences(**booking_request.dict())
        success = await bot.find_and_book_tickets(preferences)
        
        if success:
            return {"status": "success", "message": "Tickets booked successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to book tickets")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_events(query: str):
    """Search for events."""
    try:
        events = await bot.search_events(query)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/seats/{event_id}")
async def get_seats(event_id: str):
    """Get available seats for an event."""
    try:
        seats = await bot.get_available_seats(event_id)
        return {"seats": [seat.dict() for seat in seats]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 