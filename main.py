from fastapi import FastAPI
from api.manual import router as manual_router
from api.agents import router as agents_router

app = FastAPI(title="Talk2MyDB", description="NL to SQL or graphDB")

app.include_router(manual_router, prefix="/api", tags=["Manual Queries"])
app.include_router(agents_router, prefix="/api", tags=["Agents"])

@app.get("/")
async def root():
    return {"message": "Healthy connection"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
