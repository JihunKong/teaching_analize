from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Test Service - Nixpacks")

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "Nixpacks deployment successful!",
        "version": "TEST-NIXPACKS-v1",
        "timestamp": datetime.now().isoformat(),
        "port": int(os.environ.get('PORT', 8080)),
        "deployed": "2025-08-15-NIXPACKS"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "NIXPACKS"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))