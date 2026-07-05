from google.generativeai.types import FunctionDeclaration, Tool
from backend.tools.manual_tools import get_company_policy, get_order_status, update_ticket_state

# Schema declarations
get_policy_func = FunctionDeclaration(
    name="get_company_policy",
    description="사내 규정, 정책, 매뉴얼을 조회합니다.",
    parameters={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "조회할 정책 주제 (예: '환불규정', '배송안내', '멤버십', 'A/S')"
            }
        },
        "required": ["topic"]
    }
)

get_order_status_func = FunctionDeclaration(
    name="get_order_status",
    description="특정 고객의 주문 상태(주문번호, 상품명, 상태, 택배사 등)를 조회합니다.",
    parameters={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "고객의 주문 고유 번호 (예: 'order_123', 'order_456')"
            }
        },
        "required": ["order_id"]
    }
)

update_ticket_state_func = FunctionDeclaration(
    name="update_ticket_state",
    description="Updates the internal customer ticket state. Call this tool WHENEVER you learn new information about the customer's intent, order number, urgency, or situation.",
    parameters={
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "High level intent (e.g., 'refund_request', 'shipping_inquiry', 'general_question')"
            },
            "order_number": {
                "type": "string",
                "description": "The specific order ID if known. Leave blank if unknown."
            },
            "urgency": {
                "type": "string",
                "description": "'Low', 'Medium', or 'High'"
            },
            "summary": {
                "type": "string",
                "description": "A 1-2 sentence summary of the current state of the customer's issue."
            }
        },
        "required": ["intent", "order_number", "urgency", "summary"]
    }
)

# Tool domains
POLICY_TOOLS = Tool(function_declarations=[get_policy_func])
ORDER_TOOLS = Tool(function_declarations=[get_order_status_func])
GLOBAL_TOOLS = Tool(function_declarations=[update_ticket_state_func])

# Registry to map tool names to actual python functions
TOOL_REGISTRY = {
    "get_company_policy": get_company_policy,
    "get_order_status": get_order_status,
    "update_ticket_state": update_ticket_state
}
