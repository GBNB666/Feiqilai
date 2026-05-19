import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface Props {
  onBack?: () => void
  onNext?: () => void
  backLabel?: string
  nextLabel?: string
  backDisabled?: boolean
  nextDisabled?: boolean
}

export function StepNavigation({ onBack, onNext, backLabel = "上一步", nextLabel = "下一步", backDisabled, nextDisabled }: Props) {
  return (
    <div className="flex items-center justify-between py-3">
      {onBack ? (
        <Button variant="outline" size="sm" onClick={onBack} disabled={backDisabled}>
          <ChevronLeft className="w-4 h-4 mr-1" />
          {backLabel}
        </Button>
      ) : (
        <div />
      )}
      {onNext ? (
        <Button size="sm" onClick={onNext} disabled={nextDisabled}>
          {nextLabel}
          <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      ) : (
        <div />
      )}
    </div>
  )
}
