import Link from 'next/link';

export const metadata = {
    title: 'Refund Policy | InterviewMate',
};

export default function RefundPage() {
    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="bg-white rounded-lg shadow-md p-8 sm:p-12">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">Refund Policy</h1>
                    <p className="text-sm text-gray-500 mb-8">Last Updated: May 24, 2026</p>

                    <section className="space-y-8 text-gray-700 leading-relaxed">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">7-Day Money-Back Guarantee</h2>
                            <p>
                                We stand behind InterviewMate. If you&apos;re not satisfied with your purchase
                                for any reason, you can request a full refund within <strong>7 days</strong> of
                                the purchase date.
                            </p>
                            <p className="mt-2">This applies to all purchases:</p>
                            <ul className="list-disc pl-6 mt-2 space-y-1">
                                <li>Interview credits (Starter, Popular, Pro packs)</li>
                                <li>One-time features (AI Generator, Q&amp;A Management)</li>
                            </ul>
                        </div>

                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">How to Request a Refund</h2>
                            <p>
                                Email{' '}
                                <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                                    info@birth2death.com
                                </a>{' '}
                                within 7 days of purchase with:
                            </p>
                            <ul className="list-disc pl-6 mt-2 space-y-1">
                                <li>Your account email</li>
                                <li>The transaction ID or order number from your purchase confirmation</li>
                                <li>(Optional) A note about why — your feedback helps us improve</li>
                            </ul>
                            <p className="mt-2">
                                We&apos;ll process approved refunds within 5–10 business days back to your original payment method.
                            </p>
                        </div>

                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">What&apos;s Covered</h2>
                            <ul className="space-y-1">
                                <li>✅ Change of mind</li>
                                <li>✅ Service didn&apos;t meet your expectations</li>
                                <li>✅ Technical issues that prevented you from using the product</li>
                                <li>✅ Duplicate or unauthorized charges</li>
                            </ul>
                        </div>

                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">What&apos;s Not Covered</h2>
                            <ul className="space-y-1">
                                <li>❌ Requests made more than 7 days after purchase</li>
                                <li>❌ Free trial credits (these are already free)</li>
                                <li>❌ Accounts terminated for fraud, abuse, or violation of our Terms</li>
                            </ul>
                        </div>

                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">Free Trial</h2>
                            <p>
                                Every new account receives <strong>30 free interview credits</strong> to try
                                InterviewMate. Use them to evaluate the product before any paid purchase — that&apos;s
                                why we offer the free trial.
                            </p>
                        </div>

                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">Chargebacks</h2>
                            <p>
                                Please contact us first at{' '}
                                <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                                    info@birth2death.com
                                </a>{' '}
                                before initiating a chargeback with your bank. We&apos;ll work to resolve any
                                issue. Filing a chargeback without first contacting us may result in account
                                termination.
                            </p>
                        </div>

                        <div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">Questions?</h2>
                            <p>
                                Email{' '}
                                <a href="mailto:info@birth2death.com" className="text-blue-600 hover:text-blue-700 underline">
                                    info@birth2death.com
                                </a>{' '}
                                — we read every message and reply within 1–2 business days.
                            </p>
                        </div>

                        <div className="pt-6 border-t border-gray-200 text-sm text-gray-500 italic">
                            By creating an account or making a purchase, you agree to this Refund Policy.
                        </div>
                    </section>

                    <div className="mt-12 text-center">
                        <Link href="/" className="text-blue-600 hover:text-blue-700 font-medium">
                            ← Back to Home
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
