import { Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { getDownloadUrl } from "@/services/api"

interface Props {
  jobId: string
  filename: string
}

export function DownloadButton({ jobId, filename }: Props) {
  return (
    <a href={getDownloadUrl(jobId)} download={`formatted_${filename}`}>
      <Button className="w-full" size="lg">
        <Download className="w-5 h-5 mr-2" />下载排版后的文件
      </Button>
    </a>
  )
}
