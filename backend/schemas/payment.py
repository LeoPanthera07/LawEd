from typing import Optional

from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    payment_type: str
    query_id: Optional[str] = None


class CreateOrderResponse(BaseModel):
    razorpay_order_id: str
    amount_paise: int
    currency: str = "INR"
    payment_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    payment_id: str
    status: str
    amount_paise: int
