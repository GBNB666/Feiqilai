/**
 * 支付 Hook 占位 (Payment Hook Stub)
 * 未来集成 XPay 时取消注释下方逻辑。
 * 详见 backend/app/services/payment_stub.py
 */
import { useState } from "react"

type PaymentState = "idle" | "creating" | "pending" | "paid" | "error"

export function usePayment() {
  const [state, _setState] = useState<PaymentState>("idle")
  const [error, _setError] = useState("")

  // 未来启用:
  // import { api } from "@/services/api"
  // import type { PaymentOrder } from "@/types"
  //
  // const createOrder = async (jobId: string) => { ... }
  // const checkPayment = async (jobId: string) => { ... }

  return { state, error }
}
