from pydantic import BaseModel
from datetime import datetime


class PaymentCreateRequest(BaseModel):
    job_id: str


class PaymentResponse(BaseModel):
    id: str
    job_id: str
    xpay_order_id: str
    amount: float
    paid: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentCallbackRequest(BaseModel):
    order_id: str
    status: str
    signature: str
