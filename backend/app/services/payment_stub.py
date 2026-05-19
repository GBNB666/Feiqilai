"""
支付模块占位文件 (Payment Stub)
================================
未来集成 XPay 个人收款系统时在此实现。
XPay 是 Java Spring Boot 应用，通过 HTTP API 交互。

计划对接端点：
- POST /pay/add     — 创建支付订单
- GET  /pay/state/{id} — 查询支付状态

当前版本不包含支付功能，排版服务免费使用。

TODO (future):
1. 在 backend/.env 中配置 XPAY_BASE_URL
2. 实现 create_order(job_id) -> 调用 XPay API
3. 实现 check_payment(order_id) -> 轮询支付状态
4. 在 main.py 中注册 payment router
5. 在前端 ProcessPage 中恢复 PaymentModal
"""
