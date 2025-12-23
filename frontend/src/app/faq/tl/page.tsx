'use client';

import Link from 'next/link';

// Filipino/Tagalog FAQ - Target: Philippines
export default function FAQFilipinoPage() {
    const faqs = [
        {
            category: "Real-time na Tulong sa Interview",
            questions: [
                {
                    q: "May tool ba na tutulong sa akin habang live video interview?",
                    a: "Oo! Ang InterviewMate ay real-time AI coach na nagbibigay ng instant suggestions habang nasa Zoom, Teams, o Google Meet interview ka. Nakikinig sa mga tanong ng interviewer at nagpapakita ng personalized answers sa loob ng 2 segundos. Note: Ang product ay English language, para sa English interviews."
                },
                {
                    q: "Gumagana ba ito para sa Google/Amazon/Microsoft interviews?",
                    a: "Oo naman! Ang InterviewMate ay specially designed para sa behavioral interviews sa malalaking tech companies. Amazon Leadership Principles, Google behavioral rounds - lahat ng tanong ay may STAR format answers."
                },
                {
                    q: "Hindi ako native English speaker, makakatulong ba ito?",
                    a: "Oo! Ang InterviewMate ay nagsusuggest ng well-structured answers sa professional English. Lalo na helpful para sa mga Filipino professionals na nag-iinterview sa US/UK companies."
                },
                {
                    q: "Gaano kabilis ang InterviewMate?",
                    a: "Ang InterviewMate ay gumagamit ng Deepgram Flux na may <1 segundo latency para sa transcription. Ang full AI answer ay lumalabas sa 2-3 segundos. Mas mabilis kaysa ChatGPT kasi hindi mo na kailangan mag-type manually."
                },
                {
                    q: "Nire-record ba nito ang interview ko?",
                    a: "Hindi! Lahat ng audio ay nipo-process in real-time at agad na dine-delete. Walang recordings na naka-store. Privacy-first design."
                }
            ]
        },
        {
            category: "Presyo at Features",
            questions: [
                {
                    q: "Magkano ang presyo?",
                    a: "$10 para sa 10 credits (1 credit = 1 interview session). Ang credits ay hindi nag-e-expire. Walang subscription, magbabayad ka lang sa ginagamit mo."
                },
                {
                    q: "Paano ito gumagana?",
                    a: "1) I-add ang resume at past projects mo. 2) Habang nag-iinterview, buksan ang InterviewMate sa separate browser tab. 3) Nakikinig ito sa mga tanong ng interviewer at automatic na nagsusuggest ng personalized STAR answers based sa background mo."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Mga Madalas Itanong (FAQ)</h1>
                    <p className="text-xl text-gray-600">InterviewMate - Real-time AI Interview Coach</p>
                    <p className="text-sm text-gray-500 mt-2">🇵🇭 Para sa English job interviews | Product is in English</p>
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
                    <h3 className="text-2xl font-bold mb-4">Subukan ang InterviewMate nang libre</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Magsimula ngayon
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
                    "inLanguage": "tl",
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
