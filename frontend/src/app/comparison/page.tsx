'use client';

import Link from 'next/link';

export default function ComparisonPage() {
    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        InterviewMate vs Practice Platforms
                    </h1>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Understand the difference between real-time interview assistance and practice platforms
                    </p>
                </div>

                <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-6 mb-12">
                    <h2 className="text-2xl font-bold text-blue-900 mb-3">
                        Key Difference: Practice vs Live Assistance
                    </h2>
                    <p className="text-blue-800 text-lg">
                        <span className="font-bold">Practice platforms</span> help you prepare BEFORE interviews with mock questions and feedback.
                        <br/>
                        <span className="font-bold">InterviewMate</span> assists you DURING real interviews on Zoom/Teams/Meet - job interviews, PhD defenses, visa interviews, and more.
                    </p>
                </div>

                <div className="overflow-x-auto mb-12">
                    <table className="w-full bg-white rounded-lg shadow-md">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="px-6 py-4 text-left">Feature</th>
                                <th className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    <div className="font-bold text-blue-900">InterviewMate</div>
                                    <div className="text-sm text-blue-700">(Real-time Assistance)</div>
                                </th>
                                <th className="px-6 py-4 text-center">
                                    <div className="font-bold">Practice Platforms</div>
                                    <div className="text-sm text-gray-600">(Mock Interview Tools)</div>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className="border-t">
                                <td className="px-6 py-4 font-semibold">When to use</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    DURING actual video interview
                                </td>
                                <td className="px-6 py-4 text-center">BEFORE interview (practice)</td>
                            </tr>
                            <tr className="border-t bg-gray-50">
                                <td className="px-6 py-4 font-semibold">Works on</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    Live Zoom, Teams, Google Meet calls
                                </td>
                                <td className="px-6 py-4 text-center">Platform's own interface</td>
                            </tr>
                            <tr className="border-t">
                                <td className="px-6 py-4 font-semibold">Use case</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    Get AI help during any live interview
                                </td>
                                <td className="px-6 py-4 text-center">Practice with AI interviewer</td>
                            </tr>
                            <tr className="border-t bg-gray-50">
                                <td className="px-6 py-4 font-semibold">Response speed</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    2 seconds (real-time)
                                </td>
                                <td className="px-6 py-4 text-center">Post-practice feedback</td>
                            </tr>
                            <tr className="border-t">
                                <td className="px-6 py-4 font-semibold">Target users</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    Candidates in actual interviews
                                </td>
                                <td className="px-6 py-4 text-center">Candidates preparing for interviews</td>
                            </tr>
                            <tr className="border-t bg-gray-50">
                                <td className="px-6 py-4 font-semibold">Technology</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    Deepgram Flux + Claude 3.5 Sonnet
                                </td>
                                <td className="px-6 py-4 text-center">Various AI models</td>
                            </tr>
                            <tr className="border-t">
                                <td className="px-6 py-4 font-semibold">Latency critical</td>
                                <td className="px-6 py-4 text-center bg-blue-50 border-l-4 border-blue-500">
                                    Yes (&lt;2s required)
                                </td>
                                <td className="px-6 py-4 text-center">No (offline analysis)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div className="grid md:grid-cols-2 gap-8 mb-12">
                    <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-green-500">
                        <h3 className="text-xl font-bold text-gray-900 mb-4">When to use InterviewMate</h3>
                        <ul className="space-y-2 text-gray-700">
                            <li>• You have a scheduled interview (job, PhD, visa, school)</li>
                            <li>• Interview is on Zoom, Teams, or Google Meet</li>
                            <li>• You want real-time answer suggestions during the call</li>
                            <li>• PhD defense or committee meeting</li>
                            <li>• Visa/immigration interview at embassy</li>
                        </ul>
                    </div>

                    <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-gray-400">
                        <h3 className="text-xl font-bold text-gray-900 mb-4">When to use Practice Platforms</h3>
                        <ul className="space-y-2 text-gray-700">
                            <li>• You want to practice before the interview</li>
                            <li>• Get feedback on your answers</li>
                            <li>• Build confidence with mock interviews</li>
                            <li>• Learn common interview patterns</li>
                            <li>• No scheduled interview yet</li>
                        </ul>
                    </div>
                </div>

                <div className="bg-green-50 border-2 border-green-500 rounded-lg p-8 mb-12">
                    <h2 className="text-2xl font-bold text-green-900 mb-4">Why InterviewMate is Different</h2>
                    <div className="grid md:grid-cols-2 gap-6 text-green-800">
                        <div>
                            <h4 className="font-bold mb-2">Real Interviews Only</h4>
                            <p className="text-sm">
                                Works only during actual video calls. No mock interviews, no simulations.
                                Open InterviewMate in a separate tab while on your Zoom call.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-bold mb-2">Ultra-Low Latency</h4>
                            <p className="text-sm">
                                Uses Deepgram Flux (sub-second transcription) + Claude 3.5 Sonnet.
                                Get full AI answer in 2 seconds. Fast enough to use during live conversation.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-bold mb-2">Personalized to Your Context</h4>
                            <p className="text-sm">
                                Upload your resume, research papers, projects. AI generates answers based on YOUR actual background,
                                not generic templates.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-bold mb-2">Works for Any Interview</h4>
                            <p className="text-sm">
                                Job interviews, PhD defenses, visa interviews, school admissions.
                                Any video call where you need real-time AI assistance.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="text-center bg-blue-50 rounded-lg p-8 mb-12">
                    <h3 className="text-2xl font-bold mb-4">Ready for your next interview?</h3>
                    <Link href="/auth/register" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700">
                        Get Started with InterviewMate
                    </Link>
                </div>

                <div className="text-center">
                    <Link href="/" className="text-blue-600 hover:text-blue-700">← Back to Home</Link>
                    {' | '}
                    <Link href="/faq" className="text-blue-600 hover:text-blue-700">FAQ</Link>
                    {' | '}
                    <Link href="/pricing" className="text-blue-600 hover:text-blue-700">Pricing</Link>
                </div>
            </div>
        </div>
    );
}
