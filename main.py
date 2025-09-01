
@app.get("/api/v1/debug/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}

