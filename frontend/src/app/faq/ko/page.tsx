'use client';

import Link from 'next/link';

// Korean FAQ - Target: South Korea
export default function FAQKoreanPage() {
    const faqs = [
        {
            category: "실시간 면접 도움",
            questions: [
                {
                    q: "화상면접 때 실시간으로 도와주는 서비스 있어?",
                    a: "있습니다! InterviewMate는 Zoom, Teams, Google Meet에서 진행되는 면접 중 실시간으로 조언을 제공하는 AI 코치입니다. 면접관의 질문을 듣고 2초 이내에 맞춤형 답변을 보여줍니다. 참고: 제품은 영어로만 제공되며, 영어 면접용입니다."
                },
                {
                    q: "Google/Amazon/Microsoft 같은 대기업 면접에도 사용할 수 있나요?",
                    a: "물론입니다! InterviewMate는 특히 대형 IT 기업의 행동 면접(behavioral interview)을 위해 설계되었습니다. Amazon의 Leadership Principles, Google의 행동 면접 - 모든 질문에 대해 STAR 형식으로 답변을 제안합니다."
                },
                {
                    q: "영어가 모국어가 아닌데, 도움이 될까요?",
                    a: "네! InterviewMate는 전문적인 영어로 잘 구조화된 답변을 제안합니다. 미국/영국 기업에 면접을 보는 한국 전문가들에게 특히 유용합니다."
                },
                {
                    q: "InterviewMate의 응답 속도는 얼마나 빠른가요?",
                    a: "InterviewMate는 Deepgram Flux를 사용하여 <1초 지연으로 음성을 텍스트로 변환합니다. 완전한 AI 답변은 2-3초 내에 나타납니다. 수동으로 입력할 필요가 없기 때문에 ChatGPT보다 훨씬 빠릅니다."
                },
                {
                    q: "내 면접을 녹음하나요?",
                    a: "아니요! 모든 오디오는 실시간으로 처리되고 즉시 삭제됩니다. 어떠한 녹음도 저장되지 않습니다. 개인정보 보호를 최우선으로 하는 설계입니다."
                }
            ]
        },
        {
            category: "가격 및 기능",
            questions: [
                {
                    q: "가격은 얼마인가요?",
                    a: "$10에 10 크레딧 (1 크레딧 = 1 면접 세션). 크레딧은 절대 만료되지 않습니다. 구독 없음, 사용한 만큼만 지불하면 됩니다."
                },
                {
                    q: "어떻게 작동하나요?",
                    a: "1) 이력서와 과거 프로젝트를 추가합니다. 2) 면접 중 별도의 브라우저 탭에서 InterviewMate를 엽니다. 3) 면접관의 질문을 듣고 자동으로 귀하의 배경을 기반으로 맞춤형 STAR 답변을 제안합니다."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">자주 묻는 질문 (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - 실시간 AI 면접 코치</p>
                    <p className="text-sm text-gray-500 mt-2">🇰🇷 영어 취업 면접용 | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">InterviewMate 무료로 체험하기</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        시작하기
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">홈</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "ko",
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
