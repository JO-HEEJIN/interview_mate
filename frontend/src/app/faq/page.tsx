import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
    title: 'FAQ | InterviewMate',
    description:
        'How InterviewMate practice sessions work, responsible use in formal assessments, pricing, and what data is stored.',
    alternates: { canonical: '/faq' },
};

export default function FAQPage() {
    const faqs = [
        {
            category: "Using InterviewMate",
            questions: [
                {
                    q: "What is InterviewMate for?",
                    a: "Interview preparation and mock sessions. You add your real background and target role, generate personalized practice questions, and rehearse timed sessions where your spoken questions are transcribed in real time and the AI offers response suggestions grounded in your prepared context."
                },
                {
                    q: "Can I use InterviewMate during a real interview, exam, or admissions process?",
                    a: "Use InterviewMate for preparation, rehearsal, and settings where AI assistance is permitted. For any formal interview, assessment, examination, admissions or immigration process, follow the organizer's rules and disclose AI assistance when required. Do not use it to present AI-generated content as your own where that is not allowed."
                },
                {
                    q: "How does a practice session work?",
                    a: "Start a session, then ask yourself a question out loud, have a practice partner ask it, or play recorded questions. InterviewMate transcribes the question, looks for a matching answer in your prepared Q&A pairs, and otherwise streams a response suggestion. Compare it with your own answer, refine your Q&A pairs, and repeat."
                },
                {
                    q: "What does \"Capture audio from another tab or app\" do?",
                    a: "It lets the browser share audio from another tab or application, for example a practice partner on a video call or a recorded question set, so those questions are transcribed along with your microphone. The browser always asks for your permission first."
                },
                {
                    q: "Does InterviewMate work on mobile phones?",
                    a: "InterviewMate is designed for desktop browsers. Mobile browsers are not currently supported."
                }
            ]
        },
        {
            category: "Technology",
            questions: [
                {
                    q: "What technology does InterviewMate use?",
                    a: "Deepgram for streaming speech-to-text, OpenAI embeddings with a Qdrant vector database for searching your prepared Q&A pairs, and Anthropic Claude for streamed response suggestions. The engineering case study describes the pipeline, its latency budget, and its known gaps."
                },
                {
                    q: "How does InterviewMate personalize response suggestions?",
                    a: "It searches only your own prepared Q&A pairs and profile context. A close match returns your prepared answer directly; otherwise the model generates a suggestion that references your background."
                },
                {
                    q: "What happens if I haven't added my background yet?",
                    a: "Suggestions will contain placeholders like [your specific project] for you to fill in with your own details. Adding real context through AI Generate or Q&A Pairs makes suggestions specific to you."
                }
            ]
        },
        {
            category: "Pricing & Credits",
            questions: [
                {
                    q: "How does the credit system work?",
                    a: "Each practice session uses 1 credit when you press 'Start Recording'. Credits never expire. There are no subscriptions."
                },
                {
                    q: "Can I get a refund?",
                    a: "Yes. We offer a 7-day money-back guarantee on all purchases, both credits and one-time features. Email info@birth2death.com within 7 days of purchase with your transaction ID. See the Refund Policy for details."
                },
                {
                    q: "What's the difference between credits and one-time features?",
                    a: "Session credits are used one per practice session. One-time features like the AI Q&A Generator are purchased once."
                }
            ]
        },
        {
            category: "Privacy & Data",
            questions: [
                {
                    q: "Does InterviewMate record my audio?",
                    a: "Audio is streamed through our server to Deepgram for transcription while a session is running. InterviewMate does not save audio recordings. The resulting transcripts are saved, as described below."
                },
                {
                    q: "What data does InterviewMate store?",
                    a: "Your account information; the background, documents, STAR stories, and Q&A pairs you add; and practice session history, including transcribed questions and response suggestions, so you can review and export it. You can delete a session and its messages from the Sessions page."
                },
                {
                    q: "Is my data kept separate from other users?",
                    a: "Yes. Vector searches are filtered by your user ID, and the API only returns or changes profiles, Q&A pairs, and sessions that belong to your signed-in account."
                }
            ]
        }
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Frequently Asked Questions
                    </h1>
                    <p className="text-xl text-gray-600">
                        Everything you need to know about InterviewMate
                    </p>
                </div>

                {/* FAQ Categories */}
                <div className="space-y-12">
                    {faqs.map((category, idx) => (
                        <div key={idx} className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-4">
                                {category.category}
                            </h2>
                            <div className="space-y-6">
                                {category.questions.map((faq, qIdx) => (
                                    <div key={qIdx} className="border-l-4 border-blue-500 pl-4">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                            {faq.q}
                                        </h3>
                                        <p className="text-gray-700 leading-relaxed">
                                            {faq.a}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* CTA */}
                <div className="mt-12 text-center bg-blue-50 rounded-lg p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-4">
                        Still have questions?
                    </h3>
                    <p className="text-gray-600 mb-6">
                        Contact us at{' '}
                        <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                            info@birth2death.com
                        </a>{' '}
                        or start practicing for free
                    </p>
                    <Link
                        href="/auth/register"
                        className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                    >
                        Get Started Free
                    </Link>
                </div>

                {/* Back to Home */}
                <div className="text-center mt-8">
                    <Link
                        href="/"
                        className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                        ← Back to Home
                    </Link>
                </div>
            </div>

            {/* Schema.org FAQ Markup */}
            <script
                type="application/ld+json"
                dangerouslySetInnerHTML={{
                    __html: JSON.stringify({
                        "@context": "https://schema.org",
                        "@type": "FAQPage",
                        "mainEntity": faqs.flatMap(category =>
                            category.questions.map(faq => ({
                                "@type": "Question",
                                "name": faq.q,
                                "acceptedAnswer": {
                                    "@type": "Answer",
                                    "text": faq.a
                                }
                            }))
                        )
                    })
                }}
            />
        </div>
    );
}
