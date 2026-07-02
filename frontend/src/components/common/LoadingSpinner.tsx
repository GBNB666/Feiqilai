interface Props {
  message?: string;
}

export default function LoadingSpinner({ message = "处理中..." }: Props) {
  return (
    <div className="flex flex-col items-center gap-5 py-20 animate-fade-in">
      {/* Spinner with pulsing ring */}
      <div className="relative">
        <div className="h-12 w-12 animate-spin rounded-full border-[3px] border-indigo-200 border-t-indigo-600" />
        <div className="absolute inset-0 rounded-full border-[3px] border-indigo-100 animate-ping opacity-30" />
      </div>
      <p className="text-gray-500 text-sm font-medium">{message}</p>
      <div className="flex gap-1.5">
        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0s" }} />
        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0.1s" }} />
        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0.2s" }} />
      </div>
    </div>
  );
}
