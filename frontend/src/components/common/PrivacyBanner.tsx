export default function PrivacyBanner() {
  return (
    <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3.5 flex items-start gap-3 animate-fade-in-up">
      {/* Lock icon — SVG replacing emoji */}
      <div className="shrink-0 mt-0.5 w-5 h-5 flex items-center justify-center">
        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <p className="text-sm text-green-800 leading-relaxed">
        <span className="font-semibold">隐私承诺：</span>
        您的论文仅用于本次格式排版处理。我们不会存储、复制、传播您的论文内容，处理完成后原稿和排版结果均不会保存在服务器上。
      </p>
    </div>
  );
}
