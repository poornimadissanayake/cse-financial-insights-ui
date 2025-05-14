from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import companies, chat

app = FastAPI(
    title="Financial Dashboard API",
    description="API for accessing company financial data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router, prefix="/api", tags=["companies"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to Financial Dashboard API"} 