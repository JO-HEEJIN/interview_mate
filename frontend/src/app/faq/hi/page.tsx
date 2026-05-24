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
                    a: "हां, InterviewMate एक रियल-टाइम AI कोच है जो आपके Zoom, Teams, या Google Meet इंटरव्यू के दौरान तुरंत सुझाव देता है। Job interviews, PhD defense, visa interviews, admission interviews - सभी के लिए काम करता है। Note: Product English में है।"
                },
                {
                    q: "किस तरह के interviews में यह काम करता है?",
                    a: "सभी तरह के interviews में! Job interviews (tech, consulting, finance), PhD defense और academic committee meetings, visa/immigration interviews, school admissions (MBA, graduate, undergraduate)। जहां भी real-time AI help चाहिए।"
                },
                {
                    q: "क्या PhD defense में भी मदद मिलेगी?",
                    a: "हां! अपनी thesis, research papers upload करें। InterviewMate आपको research methodology explain करने, conclusions defend करने, और committee के questions answer करने में real-time help देगा।"
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
                    a: "30 trial sessions के साथ मुफ्त शुरू करें। Paid packs: 25 sessions $5, 60 sessions $10, 150 sessions $20। Credits कभी expire नहीं होते। No subscription, pay only for what you use। सभी खरीदारी पर 7-day refund guarantee।"
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
                    <p className="text-gray-600 mb-6">
                        Questions or issues? Email us at{' '}
                        <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                            info@birth2death.com
                        </a>
                        . 7-day refund guarantee.
                    </p>
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
