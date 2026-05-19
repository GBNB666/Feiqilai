import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { FileQuestion } from "lucide-react"

export function NotFoundPage() {
  return (
    <div className="text-center py-16 space-y-4">
      <FileQuestion className="w-16 h-16 text-muted-foreground mx-auto" />
      <h1 className="text-2xl font-bold">页面不存在</h1>
      <p className="text-muted-foreground">您访问的页面可能已被移除或链接错误</p>
      <Link to="/"><Button>返回首页</Button></Link>
    </div>
  )
}
