'use client';

import Link from 'next/link';

// Mandarin Chinese FAQ - Target: China, Taiwan, Singapore
export default function FAQChinesePage() {
    const faqs = [
        {
            category: "实时面试辅助",
            questions: [
                {
                    q: "有没有工具可以在视频面试时实时帮助我？",
                    a: "有的！InterviewMate 是一个实时 AI 面试教练，在您进行 Zoom、Teams 或 Google Meet 面试时提供即时建议。它会听面试官的问题，并在 2 秒内显示个性化答案。注意：产品为英文版，适用于英语面试。"
                },
                {
                    q: "这个工具适合 Google/Amazon/Microsoft 等大公司的面试吗？",
                    a: "完全适合！InterviewMate 专为大型科技公司的行为面试设计。Amazon 的领导力原则面试、Google 的行为面试 - 所有问题都会用 STAR 格式建议答案。"
                },
                {
                    q: "我英语不是母语，这个工具能帮到我吗？",
                    a: "当然！InterviewMate 会用专业英语给您提供结构良好的答案建议。这对在美国/英国公司面试的中国专业人士特别有帮助。"
                },
                {
                    q: "InterviewMate 的响应速度有多快？",
                    a: "InterviewMate 使用 Deepgram Flux，转录延迟 <1 秒。完整的 AI 答案会在 2-3 秒内出现。比 ChatGPT 快得多，因为不需要手动输入。"
                },
                {
                    q: "这个工具会录制我的面试吗？",
                    a: "不会！所有音频都是实时处理，立即删除。不存储任何录音。隐私优先设计。"
                }
            ]
        },
        {
            category: "定价与功能",
            questions: [
                {
                    q: "价格是多少？",
                    a: "$10 可获得 10 个积分（1 积分 = 1 次面试）。积分永不过期。无订阅费用，仅为使用付费。"
                },
                {
                    q: "如何工作？",
                    a: "1) 添加您的简历和过去的项目。2) 面试期间，在单独的浏览器标签中打开 InterviewMate。3) 它会听面试官的问题，并自动根据您的背景建议个性化的 STAR 答案。"
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">常见问题 (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - 实时 AI 面试教练</p>
                    <p className="text-sm text-gray-500 mt-2">🇨🇳 适用于英语求职面试 | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">免费试用 InterviewMate</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        立即开始
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">首页</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "zh",
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
