import json
import google.generativeai as genai
from typing import List
from google.generativeai.types import Tool
from backend.tools.tool_registry import POLICY_TOOLS, ORDER_TOOLS, GLOBAL_TOOLS

async def get_tools_for_intent(user_message: str, mode: str = "llm", router_model: str = "gemini-2.5-flash") -> List[Tool]:
    """
    Classify the user's intent and dynamically select the most appropriate Tool Set.
    Supports two modes: "llm" (Semantic Router) and "keyword" (Heuristic).
    """
    
    tools_to_inject = [GLOBAL_TOOLS]
    
    if mode == "keyword":
        # Check if the user is asking about company policies
        policy_keywords = ["규정", "정책", "안내", "어떻게", "환불", "배송", "멤버십", "A/S", "설명", "알려줘"]
        if any(keyword in user_message for keyword in policy_keywords):
            tools_to_inject.append(POLICY_TOOLS)
            
        # Check if the user is asking about order status
        order_keywords = ["주문", "배송조회", "order", "번호", "언제", "상태"]
        if any(keyword in user_message for keyword in order_keywords):
            tools_to_inject.append(ORDER_TOOLS)
            
        return tools_to_inject

    # else: mode == "llm"
    
    router_prompt = """
    You are an intelligent intent classifier for a customer service agent.
    Analyze the user's message and determine which tools they might need.
    Output a JSON array of strings containing the required tool domains.
    Available domains:
    - "POLICY": If the user asks about company policies, refunds, shipping times, memberships, or A/S.
    - "ORDER": If the user asks about checking their specific order status, tracking number, etc.
    
    If no tools are needed (e.g. general greeting), return an empty array [].
    
    Output exactly in this JSON array format (e.g., ["POLICY"] or ["POLICY", "ORDER"]).
    """
    
    # We use the selected router model
    model = genai.GenerativeModel(router_model, system_instruction=router_prompt)
    
    try:
        response = await model.generate_content_async(
            user_message,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        # Parse JSON and map to tools
        intent_list = json.loads(response.text)
        
        if "POLICY" in intent_list:
            tools_to_inject.append(POLICY_TOOLS)
        if "ORDER" in intent_list:
            tools_to_inject.append(ORDER_TOOLS)
            
        return tools_to_inject
        
    except Exception as e:
        print(f"Dispatcher error: {e}")
        # Fallback: if routing fails, just return everything to be safe.
        tools_to_inject.extend([POLICY_TOOLS, ORDER_TOOLS])
        return tools_to_inject
