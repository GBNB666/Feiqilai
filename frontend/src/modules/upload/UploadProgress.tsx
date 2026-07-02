interface Props {
  progress: number;
}

export default function UploadProgress({ progress }: Props) {
  return (
    <div className="w-full max-w-xs mx-auto">
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-600 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-500 mt-2">上传中 {progress}%</p>
    </div>
  );
}
