"""
支付路由占位 (Payment Router Stub)
未来集成 XPay 时，取消注释下方端点并实现。
详见 backend/app/services/payment_stub.py
"""
from fastapi import APIRouter

router = APIRouter()

# 未来启用:
# @router.post("/payment/create-order")
# def create_payment_order(...): ...
#
# @router.post("/payment/callback")
# def payment_callback(...): ...
#
# @router.get("/payment/status/{job_id}")
# def check_payment_status(...): ...
