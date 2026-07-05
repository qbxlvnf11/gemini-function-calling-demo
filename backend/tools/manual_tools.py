import time
import asyncio

def get_company_policy(topic: str) -> str:
    """
    Mock database retrieval for company policies.
    """
    time.sleep(1.5)
    
    policies = {
        "환불규정": "결제 후 7일 이내에는 100% 환불이 가능합니다. 단, 상품을 사용하거나 훼손한 경우에는 환불이 불가합니다.",
        "배송안내": "평일 오후 2시 이전 결제 완료 건은 당일 발송되며, 보통 1~2 영업일 이내에 배송됩니다. 도서 산간 지역은 추가 배송비가 발생할 수 있습니다.",
        "멤버십": "멤버십 등급은 브론즈, 실버, 골드, VIP로 나뉘며, 구매 금액에 따라 매월 1일에 갱신됩니다. VIP 고객에게는 상시 10% 할인 혜택이 제공됩니다.",
        "A/S": "무상 A/S 보증 기간은 구매일로부터 1년입니다. 고객 과실로 인한 파손은 유상 수리로 진행됩니다."
    }
    
    return policies.get(topic, f"'{topic}'에 대한 규정을 찾을 수 없습니다. 가능한 주제: 환불규정, 배송안내, 멤버십, A/S.")

def get_order_status(order_id: str) -> str:
    """
    Mock DB retrieval for order status.
    """
    time.sleep(1.0)
    
    # Self-Correction Trigger: Require '-KR' suffix to demonstrate retry
    if not order_id.endswith("-KR"):
        return f"System Error: Invalid format. You (the AI) must append '-KR' to the order_id and CALL THIS TOOL AGAIN IMMEDIATELY. Do NOT ask the user to provide it. Auto-correct it yourself and retry."
    
    orders = {
        "order_123-KR": "주문번호: order_123-KR, 상품명: 무선 이어폰, 상태: 배송 중 (예상 도착일: 2026-07-06), 택배사: 대한통운",
        "order_456-KR": "주문번호: order_456-KR, 상품명: 스마트 워치, 상태: 상품 준비 중 (발송 예정일: 2026-07-06)"
    }
    
    return orders.get(order_id, f"주문번호가 '{order_id}'인 주문 내역을 찾을 수 없습니다.")

def update_ticket_state(intent: str, order_number: str, urgency: str, summary: str) -> str:
    """
    Updates the internal customer ticket state. Call this tool WHENEVER you learn new information about the customer's intent, order number, urgency, or situation.
    - intent: High level intent (e.g., 'refund_request', 'shipping_inquiry', 'general_question')
    - order_number: The specific order ID if known. Leave blank if unknown.
    - urgency: 'Low', 'Medium', or 'High'
    - summary: A 1-2 sentence summary of the current state of the customer's issue.
    """
    # In a real app, this might write to a Redis/Postgres state store.
    # Here, the UI catches it via WebSocket.
    return "Ticket state successfully updated. The support dashboard now reflects these values."
