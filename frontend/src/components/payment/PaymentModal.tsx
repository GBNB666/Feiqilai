/**
 * 支付弹窗占位 (Payment Modal Stub)
 * 未来集成 XPay 时取消注释下方逻辑。
 * 详见 backend/app/services/payment_stub.py
 */
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"

interface Props {
  open: boolean
  jobId: string
  price: number
  onPaid: () => void
  onClose: () => void
}

export function PaymentModal({ open, onClose, onPaid: _onPaid }: Props) {
  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>支付功能暂未开放</DialogTitle>
          <DialogDescription>当前版本排版服务免费使用</DialogDescription>
        </DialogHeader>
        <div className="py-4 text-center text-muted-foreground text-sm">
          支付功能将在未来版本中集成 XPay 收款系统
        </div>
      </DialogContent>
    </Dialog>
  )
}
