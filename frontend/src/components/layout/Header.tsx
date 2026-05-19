import { BookOpen } from "lucide-react"

export function Header() {
  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 h-16 flex items-center gap-3">
        <BookOpen className="w-7 h-7 text-primary" />
        <div>
          <h1 className="text-lg font-bold tracking-tight">论文排版助手</h1>
          <p className="text-xs text-muted-foreground">AI驱动的学术论文智能排版</p>
        </div>
      </div>
    </header>
  )
}
