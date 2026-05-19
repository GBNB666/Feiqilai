interface Props {
  price: number
}

export function PriceDisplay({ price }: Props) {
  return (
    <div className="flex items-baseline gap-1">
      <span className="text-3xl font-bold">&yen;{price}</span>
      <span className="text-sm text-muted-foreground">/次</span>
    </div>
  )
}
