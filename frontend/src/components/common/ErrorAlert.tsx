interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ErrorAlert({ message, onRetry }: Props) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <p className="text-red-700 text-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 text-sm font-medium text-red-600 hover:text-red-800 underline"
        >
          重试
        </button>
      )}
    </div>
  );
}
