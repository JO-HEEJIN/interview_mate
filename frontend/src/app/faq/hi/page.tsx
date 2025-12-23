'use client';

import Link from 'next/link';

// Hindi FAQ - Target: India (huge market for English job interviews)
export default function FAQHindiPage() {
    const faqs = [
        {
            category: "वीडियो इंटरव्यू के दौरान मदद",
            questions: [
                {
                    q: "क्या कोई ऐसा टूल है जो लाइव वीडियो इंटरव्यू के दौरान मेरी मदद कर सके?",
                    a: "हां, InterviewMate एक रियल-टाइम AI कोच है जो आपके Zoom, Teams, या Google Meet इंटरव्यू के दौरान तुरंत सुझाव देता है। यह इंटरव्यूअर के सवालों को सुनता है और 2 सेकंड के अंदर personalized जवाब दिखाता है। Note: Product English में है, English interviews के लिए।"
                },
                {
                    q: "क्या यह Google/Amazon/Microsoft जैसी बड़ी कंपनियों के इंटरव्यू में काम करता है?",
                    a: "बिल्कुल! InterviewMate विशेष रूप से big tech companies के behavioral interviews के लिए बनाया गया है। Amazon के Leadership Principles, Google के behavioral rounds - सभी के लिए STAR format में answers suggest करता है।"
                },
                {
                    q: "मैं non-native English speaker हूं। क्या यह मेरी मदद करेगा?",
                    a: "हां! InterviewMate आपको professional English में well-structured answers suggest करता है। यह विशेष रूप से Indian professionals के लिए helpful है जो US/UK companies में interview कर रहे हैं।"
                },
                {
                    q: "InterviewMate कितनी तेज़ है?",
                    a: "InterviewMate Deepgram Flux का उपयोग करता है जो <1 second में transcription देता है। पूरा AI answer 2-3 seconds में आ जाता है। यह ChatGPT से बहुत तेज़ है क्योंकि आपको manually type नहीं करना पड़ता।"
                }
            ]
        },
        {
            category: "Technology और Pricing",
            questions: [
                {
                    q: "यह कैसे काम करता है?",
                    a: "1) आप अपना resume और past projects add करते हैं। 2) Interview के दौरान, InterviewMate एक अलग browser tab में खुला रहता है। 3) यह interviewer के questions को सुनता है और automatically आपकी background से personalized STAR answers suggest करता है।"
                },
                {
                    q: "क्या यह मेरा interview record करता है?",
                    a: "नहीं! सभी audio real-time में process होता है और तुरंत delete हो जाता है। कोई recording store नहीं होती। Privacy-first design।"
                },
                {
                    q: "Pricing क्या है?",
                    a: "$10 में 10 credits (1 credit = 1 interview session)। Credits कभी expire नहीं होते। No subscription, pay only for what you use।"
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        अक्सर पूछे जाने वाले प्रश्न (FAQ)
                    </h1>
                    <p className="text-xl text-gray-600">
                        InterviewMate - Real-time AI Interview Coach
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                        🇮🇳 English job interviews के लिए | Product is in English
                    </p>
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
                    <h3 className="text-2xl font-bold mb-4">Try InterviewMate Free</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Get Started
                    </Link>
                </div>

                <div className="text-center mt-8">
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">← English FAQ</Link>
                    {' | '}
                    <Link href="/" className="text-blue-600 hover:text-blue-700">Home</Link>
                </div>
            </div>

            <script type="application/ld+json" dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "inLanguage": "hi",
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
