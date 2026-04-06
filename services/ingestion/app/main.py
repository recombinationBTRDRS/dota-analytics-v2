from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Dota 2 Ingestion Service",
    version="1.0.0",
    description="Fetch, parse, validate and store Dota 2 matches"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ingestion",
        "version": "1.0.0"
    }

@app.get("/ready")
async def ready_check():
    """Readiness check endpoint"""
    return {
        "ready": True,
        "service": "ingestion"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )