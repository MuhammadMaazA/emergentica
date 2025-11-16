"""Minimal WebSocket test to verify FastAPI WebSocket support"""
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws-test")
async def websocket_test(websocket: WebSocket):
    print("WebSocket connection attempt!")
    await websocket.accept()
    print("WebSocket accepted!")
    await websocket.send_json({"message": "Hello from WebSocket!"})
    await websocket.close()

@app.get("/")
def root():
    return {"message": "Test server running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
