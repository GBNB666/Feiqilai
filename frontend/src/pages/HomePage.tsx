import { useNavigate } from "react-router-dom";
import { useFileUpload } from "../modules/upload/useFileUpload";
import FileUploader from "../modules/upload/FileUploader";
import ErrorAlert from "../components/common/ErrorAlert";

const STEPS = [
  { icon: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  ), label: "上传 .docx 论文" },
  { icon: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  ), label: "AI 识别章节结构" },
  { icon: (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  ), label: "自动排版并下载" },
];

export default function HomePage() {
  const navigate = useNavigate();
  const { uploading, progress, error, upload } = useFileUpload();

  const handleUpload = async (file: File) => {
    const job = await upload(file);
    if (job) {
      navigate(`/process/${job.id}`);
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-8 animate-fade-in-up">
      {/* Hero */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-gray-800 tracking-tight">
          论文格式自动排版
        </h1>
        <p className="text-gray-500 text-sm leading-relaxed max-w-md mx-auto">
          上传论文，AI 自动识别结构，按学术规范排版，一键下载
        </p>
      </div>

      {/* Uploader */}
      <div className="animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
        <FileUploader onUpload={handleUpload} uploading={uploading} progress={progress} />
      </div>

      {error && <ErrorAlert message={error} />}

      {/* Steps — SVG icons replacing numbers */}
      <div className="grid grid-cols-3 gap-4 pt-2">
        {STEPS.map((step, i) => (
          <div
            key={i}
            className="flex flex-col items-center gap-2.5 p-4 rounded-xl bg-white border border-gray-100 shadow-sm hover:shadow-md hover:border-gray-200 transition-all duration-300 hover:-translate-y-0.5"
            style={{ animationDelay: `${0.2 + i * 0.1}s` }}
          >
            <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-500 group-hover:bg-indigo-100 transition-colors">
              {step.icon}
            </div>
            <span className="text-xs text-gray-500 font-medium text-center leading-tight">
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
