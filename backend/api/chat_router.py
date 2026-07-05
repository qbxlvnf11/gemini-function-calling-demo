import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.agent.engine import ChatEngine

router = APIRouter()

# Store active sessions. In a real app, this would be tied to user/session IDs.
active_engines = {}

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = id(websocket)
    engine = ChatEngine()
    active_engines[session_id] = engine
    
    # Send welcome message
    await websocket.send_json({
        "type": "message",
        "role": "model",
        "text": "안녕하세요! 무엇을 도와드릴까요? (예: '환불규정 알려줘', 'order_123 배송 상태 조회해줘')"
    })
    
    try:
        while True:
            # Wait for user message
            raw_data = await websocket.receive_text()
            
            try:
                data = json.loads(raw_data)
                user_msg = data.get("text", "")
                selected_model = data.get("model", "gemini-2.5-flash")
                routing_mode = data.get("routing_mode", "llm")
                router_model = data.get("router_model", "gemini-2.5-flash")
            except json.JSONDecodeError:
                user_msg = raw_data
                selected_model = "gemini-2.5-flash"
                routing_mode = "llm"
                router_model = "gemini-2.5-flash"
            
            # Status callback to stream progress
            async def status_callback(status_msg: str):
                await websocket.send_json({
                    "type": "status",
                    "text": status_msg
                })
                
            async def tool_call_callback(name: str, args: dict):
                await websocket.send_json({
                    "type": "tool_call",
                    "name": name,
                    "args": args
                })
                
            async def tool_result_callback(name: str, result: str):
                await websocket.send_json({
                    "type": "tool_result",
                    "name": name,
                    "result": result
                })
                
            async def stream_callback(chunk: str):
                await websocket.send_json({
                    "type": "message_stream",
                    "text": chunk
                })
                
            async def ticket_state_callback(state: dict):
                await websocket.send_json({
                    "type": "ticket_update",
                    "data": state
                })
            
            try:
                # Process message through the engine
                final_response = await engine.process_message(
                    user_msg, 
                    selected_model, 
                    routing_mode,
                    router_model,
                    status_callback,
                    tool_call_callback,
                    tool_result_callback,
                    stream_callback,
                    ticket_state_callback
                )
                
                # Signal that streaming is complete
                await websocket.send_json({
                    "type": "message_stream_end"
                })
                
                # Clear status
                await websocket.send_json({
                    "type": "status",
                    "text": ""
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "text": f"오류가 발생했습니다: {str(e)}"
                })
                await websocket.send_json({
                    "type": "status",
                    "text": ""
                })
                
    except WebSocketDisconnect:
        if session_id in active_engines:
            del active_engines[session_id]
        print(f"Client {session_id} disconnected")
