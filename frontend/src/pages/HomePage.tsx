import { useNavigate } from "react-router-dom"
import { FileUploader } from "@/components/upload/FileUploader"
import { HistoryPanel } from "@/components/history/HistoryPanel"
import { useHistory } from "@/hooks/useHistory"

export function HomePage() {
  const navigate = useNavigate()
  const { records, addRecord, clearHistory } = useHistory()

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold tracking-tight">上传论文，开始智能排版</h1>
        <p className="text-muted-foreground max-w-md mx-auto">
          支持 .docx 和 .pdf 格式。AI 将自动识别论文结构，按学术规范排版。
        </p>
      </div>

      <FileUploader
        onUploaded={(jobId, filename, fileType) => {
          addRecord({
            jobId,
            filename: filename || "未知文件",
            fileType: fileType || "docx",
            mode: "auto",
            templateName: "默认模板",
            timestamp: Date.now(),
          })
          navigate(`/process/${jobId}`)
        }}
      />

      <div className="grid sm:grid-cols-3 gap-4 mt-12">
        {[
          { title: "AI识别", desc: "自动识别标题层级、段落结构、图表位置" },
          { title: "学术规范", desc: "按照高校和期刊论文排版规范处理" },
          { title: "即时下载", desc: "排版完成后即时下载，无需等待" },
        ].map((item) => (
          <div key={item.title} className="text-center p-4">
            <h3 className="font-semibold mb-1">{item.title}</h3>
            <p className="text-xs text-muted-foreground">{item.desc}</p>
          </div>
        ))}
      </div>

      {records.length > 0 && (
        <div className="border rounded-xl p-4">
          <HistoryPanel
            records={records}
            onClear={clearHistory}
            onOpen={(jobId) => navigate(`/process/${jobId}`)}
          />
        </div>
      )}
    </div>
  )
}
