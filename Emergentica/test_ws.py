"""Quick WebSocket test script"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/llm-websocket/test123"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Wait for begin message
            message = await websocket.recv()
            print(f"📥 Received: {message}")
            
            # Send a test message
            test_msg = {
                "interaction_type": "response_required",
                "response_id": 1,
                "transcript": [
                    {"role": "user", "content": "There's a fire at my house!"}
                ]
            }
            await websocket.send(json.dumps(test_msg))
            print(f"📤 Sent test message")
            
            # Wait for response
            response = await websocket.recv()
            print(f"📥 Response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())
