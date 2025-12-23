'use client';

import Link from 'next/link';

export default function FAQPage() {
    const faqs = [
        {
            category: "Real-time Interview Assistance",
            questions: [
                {
                    q: "Is there a tool that helps me during a live video interview?",
                    a: "Yes, InterviewMate provides real-time AI coaching during your actual interview. It listens to the interviewer's questions and instantly suggests personalized answers while you're on Zoom, Teams, or Google Meet."
                },
                {
                    q: "How fast does InterviewMate respond during an interview?",
                    a: "InterviewMate achieves <1 second latency for transcription using Deepgram Flux, with complete AI-generated answers appearing within 2-3 seconds of the interviewer finishing their question."
                },
                {
                    q: "Can I use this during a Zoom interview without the interviewer knowing?",
                    a: "InterviewMate runs in a separate browser window/tab and doesn't interfere with your video call. The AI suggestions appear on your screen only. However, users are responsible for following their company's interview policies."
                },
                {
                    q: "Does InterviewMate work on mobile phones?",
                    a: "Currently InterviewMate is optimized for desktop browsers (Chrome, Edge, Safari). Mobile support is planned for future releases."
                }
            ]
        },
        {
            category: "Technology & Performance",
            questions: [
                {
                    q: "What AI technology does InterviewMate use?",
                    a: "InterviewMate uses Deepgram Flux for real-time speech-to-text (<500ms latency) and Claude 3.5 Sonnet for intelligent answer generation. This combination delivers the fastest and highest quality responses."
                },
                {
                    q: "How does InterviewMate personalize answers to my background?",
                    a: "InterviewMate uses RAG (Retrieval Augmented Generation) with Qdrant vector database. You can add your resume, STAR stories, and prepared Q&A pairs. When answering questions, the AI semantically searches your background and incorporates specific details from your experience."
                },
                {
                    q: "What happens if I don't have any background information added?",
                    a: "The AI will generate answers with placeholders like [your specific project] or [company name] that you can fill in with your own details. You'll see a tip suggesting the AI Q&A Generator feature for fully personalized answers."
                },
                {
                    q: "Why is InterviewMate faster than other interview tools?",
                    a: "We eliminated threading bottlenecks by using fully async I/O architecture. Previous systems used background threads with 5-second timeouts. Our async implementation uses direct await calls, removing timeout issues entirely."
                }
            ]
        },
        {
            category: "Pricing & Credits",
            questions: [
                {
                    q: "How does the credit system work?",
                    a: "Each interview session consumes 1 credit when you press 'Start Recording'. Credits never expire and you can use them whenever you have an interview. No subscriptions - pay only for what you use."
                },
                {
                    q: "Can I get a refund if I don't like the service?",
                    a: "All purchases are final. We offer a strict no-refund policy for digital products. However, refunds may be considered for technical issues (system failures, duplicate charges, unauthorized transactions) if reported within 7 days."
                },
                {
                    q: "What's the difference between credits and one-time features?",
                    a: "Interview credits are consumed per session (1 credit = 1 interview). One-time features like AI Q&A Generator are purchased once and available forever."
                },
                {
                    q: "Do credits expire?",
                    a: "No, credits never expire. Buy them now and use them whenever you have interviews - next week, next month, or next year."
                }
            ]
        },
        {
            category: "Privacy & Security",
            questions: [
                {
                    q: "Does InterviewMate record or store my interview audio?",
                    a: "No. All audio is processed in real-time and immediately discarded. We use streaming transcription - audio never touches our servers or gets stored anywhere."
                },
                {
                    q: "Is my personal data safe?",
                    a: "Yes. We use strict user_id filtering in our vector database (Qdrant) to ensure complete data isolation. Your resume, STAR stories, and Q&A pairs are never shared with other users."
                },
                {
                    q: "What data does InterviewMate collect?",
                    a: "We store: (1) Your account information (email, name), (2) Your uploaded background (resume, STAR stories, Q&A pairs), (3) Interview session metadata (timestamp, credits used). We do NOT store audio recordings or transcripts."
                }
            ]
        },
        {
            category: "Use Cases",
            questions: [
                {
                    q: "What types of interviews is InterviewMate best for?",
                    a: "InterviewMate excels at behavioral interviews (Tell me about a time when...), situational questions (How would you handle...?), and general questions (What's your biggest weakness?). It provides STAR-formatted answers based on your actual experience."
                },
                {
                    q: "Can InterviewMate help with technical coding interviews?",
                    a: "Currently InterviewMate focuses on behavioral and conversational questions. For technical coding, traditional platforms like LeetCode are more suitable. However, we can help answer questions about your technical projects and design decisions."
                },
                {
                    q: "I'm interviewing at Google/Amazon/Meta - will this work?",
                    a: "Yes, InterviewMate works for interviews at any company. Many big tech companies use behavioral interviews (Amazon's Leadership Principles, Google's Googleyness). Our AI helps you structure answers using the STAR method with specific examples from your background."
                },
                {
                    q: "I'm a non-native English speaker - can InterviewMate help?",
                    a: "Absolutely. InterviewMate helps you phrase answers clearly and professionally. The AI suggests well-structured responses you can read and adapt to your speaking style."
                }
            ]
        },
        {
            category: "Comparison",
            questions: [
                {
                    q: "How is InterviewMate different from mock interview platforms?",
                    a: "Mock interviews help you practice before the interview. InterviewMate helps you DURING the actual interview when it matters most. It's real-time coaching, not practice."
                },
                {
                    q: "Why not just prepare answers beforehand?",
                    a: "You can't predict every question. Even if you prepare 50 questions, the interviewer might ask the 51st. InterviewMate handles unexpected questions in real-time."
                },
                {
                    q: "What about ChatGPT - can I just use that during interviews?",
                    a: "ChatGPT requires you to type questions manually, which takes too long during live interviews. InterviewMate automatically transcribes the interviewer's speech and generates answers instantly (<2 seconds)."
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
                        Contact us at support@interviewmate.tech or try InterviewMate for free
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
