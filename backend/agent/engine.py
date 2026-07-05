import json
import asyncio
import google.generativeai as genai
from typing import List, Dict, Any, Callable

from backend.core.config import MODEL_NAME
from backend.agent.dispatcher import get_tools_for_intent
from backend.tools.tool_registry import TOOL_REGISTRY
from backend.agent.prompts import CUSTOMER_SERVICE_PROMPT

# Configure genai in main.py, so here we assume it's already configured.

class ChatEngine:
    def __init__(self):
        self.contents = [] # Maintains strict message history
        
    async def process_message(
        self, 
        user_message: str, 
        model_name: str, 
        routing_mode: str = "llm",
        router_model: str = "gemini-2.5-flash",
        status_callback: Callable = None,
        tool_call_callback: Callable = None,
        tool_result_callback: Callable = None,
        stream_callback: Callable = None,
        ticket_state_callback: Callable = None
    ):
        """
        Process a user message using Native Function Calling loop.
        """
        # 1. Add user message to contents
        self.contents.append({"role": "user", "parts": [user_message]})
        
        # 2. Dispatcher: Select tools dynamically based on intent
        if status_callback:
            if routing_mode == "llm":
                await status_callback("LLM 기반 의도 분석(라우팅) 중...")
            else:
                await status_callback("키워드 기반 의도 분석 중...")
            
        active_tools = await get_tools_for_intent(user_message, routing_mode, router_model)
        
        if status_callback:
            await status_callback(f"의도 분석 완료: {len(active_tools)}개의 툴 세트 로드됨")
            
        model = genai.GenerativeModel(
            model_name=model_name, 
            system_instruction=CUSTOMER_SERVICE_PROMPT + "\n\nYou MUST call `update_ticket_state` WHENEVER you learn new info about the customer's intent, order_number, urgency, or situation. Keep the state updated at all times.",
            tools=active_tools if active_tools else None
        )
        
        # 3. 1차 모델 호출 (Native Call)
        if status_callback:
            await status_callback("AI 생각 중...")
            
        max_iterations = 5
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            
            # Generate response (True stream)
            response_stream = await model.generate_content_async(self.contents, stream=True)
            
            # We will collect the full response to append to history later
            has_fc = False
            full_text = ""
            full_response_parts = []
            
            async for chunk in response_stream:
                if not chunk.candidates or not chunk.candidates[0].content.parts:
                    continue
                    
                for part in chunk.candidates[0].content.parts:
                    if getattr(part, 'function_call', None):
                        has_fc = True
                        full_response_parts.append(part)
                    elif getattr(part, 'text', None):
                        full_text += part.text
                        if stream_callback and not has_fc:
                            await stream_callback(part.text)
            
            # Reconstruct the AI's response content for history
            if has_fc:
                ai_message = {"role": "model", "parts": full_response_parts}
                self.contents.append(ai_message)
                
                function_calls = [p.function_call for p in full_response_parts if getattr(p, 'function_call', None)]
                func_names = [fc.name for fc in function_calls]
                
                if status_callback:
                    prefix = "멀티 도구" if len(func_names) > 1 else "도구"
                    await status_callback(f"{prefix} 실행 중: {', '.join(func_names)} ...")
                
                async def execute_tool(fc):
                    func_name = fc.name
                    func_args = {k: v for k, v in fc.args.items()}
                    
                    if tool_call_callback:
                        await tool_call_callback(func_name, func_args)
                        
                    if func_name == "update_ticket_state" and ticket_state_callback:
                        await ticket_state_callback(func_args)
                        
                    if func_name in TOOL_REGISTRY:
                        func_to_call = TOOL_REGISTRY[func_name]
                        result_raw = await asyncio.to_thread(func_to_call, **func_args)
                        if tool_result_callback:
                            await tool_result_callback(func_name, str(result_raw))
                        return {"name": func_name, "response": {"result": result_raw}}
                    else:
                        error_msg = f"Function {func_name} not found."
                        if tool_result_callback:
                            await tool_result_callback(func_name, error_msg)
                        return {"name": func_name, "response": {"error": error_msg}}
                        
                results = await asyncio.gather(*(execute_tool(fc) for fc in function_calls))
                    
                if status_callback:
                    await status_callback(f"{len(results)}개의 도구 실행 완료! 통합 답변 생성 중...")
                    
                response_parts = [{"function_response": res} for res in results]
                self.contents.append({"role": "function", "parts": response_parts})
                
                # Loop continues to generate the next response based on tool results
                continue
            
            else:
                # No function calls, meaning the AI is providing the final answer
                self.contents.append({"role": "model", "parts": [full_text]})
                return full_text
            
        if iterations >= max_iterations and status_callback:
            await status_callback("경고: 최대 도구 호출 횟수를 초과했습니다.")
            
        return "죄송합니다. 요청을 처리하는 중에 너무 많은 단계를 거쳐 중단되었습니다."

    def get_contents_for_ui(self) -> List[Dict]:
        return self.contents
