'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function PaymentSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  const [isLoading, setIsLoading] = useState(true);
  const [sessionDetails, setSessionDetails] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      router.push('/pricing');
      return;
    }

    const fetchSessionDetails = async () => {
      try {
        const response = await fetch(`${API_URL}/api/payments/session/${sessionId}`);
        if (response.ok) {
          const data = await response.json();
          setSessionDetails(data);
        } else {
          setError('Failed to load payment details');
        }
      } catch (err) {
        setError('An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessionDetails();
  }, [sessionId, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing your payment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Error</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link
            href="/pricing"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
          >
            Back to Pricing
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        {/* Success Icon */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Payment Successful!
          </h1>
          <p className="text-gray-600">
            Thank you for your purchase
          </p>
        </div>

        {/* Payment Details */}
        {sessionDetails && (
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h2 className="font-semibold text-gray-900 mb-4">Purchase Details</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Amount Paid:</span>
                <span className="font-semibold text-gray-900">
                  ${sessionDetails.amount_total?.toFixed(2)} {sessionDetails.currency?.toUpperCase()}
                </span>
              </div>
              {sessionDetails.plan_type === 'credits' && sessionDetails.credits_amount && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Credits Added:</span>
                  <span className="font-semibold text-gray-900">
                    {sessionDetails.credits_amount} sessions
                  </span>
                </div>
              )}
              {sessionDetails.customer_email && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Receipt sent to:</span>
                  <span className="font-semibold text-gray-900">
                    {sessionDetails.customer_email}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Next Steps */}
        <div className="bg-blue-50 rounded-lg p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-2">What's Next?</h2>
          <p className="text-sm text-gray-600">
            Your credits and features have been added to your account.
            You can start using them right away!
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Link
            href="/interview"
            className="block w-full bg-blue-600 text-white text-center px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Start Interview Practice
          </Link>
          <Link
            href="/profile/qa-pairs"
            className="block w-full bg-gray-100 text-gray-900 text-center px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
          >
            Manage Q&A Pairs
          </Link>
          <Link
            href="/"
            className="block w-full text-center text-gray-600 hover:text-gray-900 py-2"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  );
}
