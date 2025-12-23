'use client';

import Link from 'next/link';

// Japanese FAQ - Target: Japan
export default function FAQJapanesePage() {
    const faqs = [
        {
            category: "リアルタイム面接サポート",
            questions: [
                {
                    q: "ビデオ面接中にリアルタイムでサポートしてくれるツールはありますか？",
                    a: "はい！InterviewMateは、Zoom、Teams、Google Meetの面接中に即座にアドバイスを提供するリアルタイムAIコーチです。面接官の質問を聞き、2秒以内にパーソナライズされた回答を表示します。注意：製品は英語版で、英語面接用です。"
                },
                {
                    q: "Google/Amazon/Microsoftなどの大手企業の面接に使えますか？",
                    a: "もちろんです！InterviewMateは、特に大手テック企業の行動面接のために設計されています。AmazonのLeadership Principles、Googleの行動面接 - すべてSTAR形式で回答を提案します。"
                },
                {
                    q: "英語がネイティブではありませんが、役に立ちますか？",
                    a: "はい！InterviewMateは、プロフェッショナルな英語で構造化された回答を提案します。米国/英国企業で面接を受ける日本人プロフェッショナルに特に役立ちます。"
                },
                {
                    q: "InterviewMateの応答速度は？",
                    a: "InterviewMateはDeepgram Fluxを使用し、<1秒で文字起こしします。完全なAI回答は2〜3秒で表示されます。手動入力が不要なため、ChatGPTよりはるかに高速です。"
                },
                {
                    q: "面接を録音しますか？",
                    a: "いいえ！すべての音声はリアルタイムで処理され、即座に削除されます。録音は保存されません。プライバシー第一の設計です。"
                }
            ]
        },
        {
            category: "価格と機能",
            questions: [
                {
                    q: "料金は？",
                    a: "$10で10クレジット（1クレジット = 1面接セッション）。クレジットは無期限。サブスクリプションなし、使用した分だけ支払い。"
                },
                {
                    q: "どのように機能しますか？",
                    a: "1) 履歴書と過去のプロジェクトを追加します。2) 面接中、別のブラウザタブでInterviewMateを開きます。3) 面接官の質問を聞き、あなたの経歴に基づいてパーソナライズされたSTAR回答を自動的に提案します。"
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">よくある質問 (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - リアルタイムAI面接コーチ</p>
                    <p className="text-sm text-gray-500 mt-2">🇯🇵 英語面接用 | Product is in English</p>
                </div>

                <div className="space-y-12">
                    {faqs.map((category, idx) => (
                        <div key={idx} className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6">{category.category}</h2>
                            <div className="space-y-6">
                                {category.questions.map((faq, qIdx) => (
                                    <div key={qIdx} className="border-l-4 border-blue-500 pl-4">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{faq.q}</h3>
                                        <p className="text-gray-700">{faq.a}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-12 text-center bg-blue-50 rounded-lg p-8">
                    <h3 className="text-2xl font-bold mb-4">InterviewMateを無料で試す</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        今すぐ始める
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">ホーム</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "ja",
                    "mainEntity": faqs.flatMap(cat => cat.questions.map(faq => ({
                        "@type": "Question",
                        "name": faq.q,
                        "acceptedAnswer": { "@type": "Answer", "text": faq.a }
                    })))
                })
            }} />
        </div>
    );
}
