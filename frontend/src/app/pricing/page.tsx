'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';

interface PricingPlan {
  id: string;
  plan_code: string;
  plan_name: string;
  plan_type: 'credits' | 'one_time';
  description: string;
  price_usd: number;
  credits_amount: number;
  features: string[];
  display_order: number;
}

interface UserFeatures {
  interview_credits: number;
  ai_generator_available: boolean;
  qa_management_available: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function PricingPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [userFeatures, setUserFeatures] = useState<UserFeatures | null>(null);
  const [processingPlan, setProcessingPlan] = useState<string | null>(null);

  // Check authentication and fetch all data in parallel
  useEffect(() => {
    const initializePage = async () => {
      // Check auth first
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push('/auth/login?redirect=/pricing');
        return;
      }
      setUserId(session.user.id);

      // Fetch plans and user features in parallel (no need to wait)
      Promise.all([
        fetch(`${API_URL}/api/subscriptions/plans`).then(res => res.ok ? res.json() : []),
        fetch(`${API_URL}/api/subscriptions/${session.user.id}/summary`).then(res => res.ok ? res.json() : null)
      ]).then(([plansData, featuresData]) => {
        setPlans(plansData);
        if (featuresData) {
          setUserFeatures({
            interview_credits: featuresData.interview_credits || 0,
            ai_generator_available: featuresData.ai_generator_available || false,
            qa_management_available: featuresData.qa_management_available || false,
          });
        }
      }).catch(error => {
        console.error('Error fetching data:', error);
      });
    };

    initializePage();
  }, [router]);

  const handlePurchase = async (planCode: string) => {
    if (!userId) {
      router.push('/auth/login?redirect=/pricing');
      return;
    }

    setProcessingPlan(planCode);

    try {
      const response = await fetch(`${API_URL}/api/lemon-squeezy/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          plan_code: planCode,
          success_url: `${window.location.origin}/payment/success`,
          cancel_url: `${window.location.origin}/pricing`,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        window.location.href = data.checkout_url;
      } else {
        alert('Failed to create checkout session. Please try again.');
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setProcessingPlan(null);
    }
  };

  const creditPacks = plans.filter(p => p.plan_type === 'credits');
  const oneTimePurchases = plans.filter(p => p.plan_type === 'one_time');

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600">
            Pay as you go. No subscriptions. No hidden fees.
          </p>
        </div>

        {/* Current Credits Display */}
        {userFeatures && (
          <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Your Credits</h3>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  {userFeatures.interview_credits} sessions
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">
                  {userFeatures.ai_generator_available && (
                    <div className="text-green-600 font-medium">✓ AI Generator</div>
                  )}
                  {userFeatures.qa_management_available && (
                    <div className="text-green-600 font-medium">✓ Q&A Management</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Interview Credit Packs */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Interview Credits
          </h2>
          <p className="text-center text-gray-600 mb-8">
            Credits for real-time AI assistance during live video interviews
          </p>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {creditPacks.map((plan) => (
              <div
                key={plan.id}
                className={`relative bg-white rounded-lg shadow-md border-2 ${
                  plan.plan_code === 'credits_popular'
                    ? 'border-blue-500 scale-105'
                    : 'border-gray-200'
                } p-6 flex flex-col`}
              >
                {plan.plan_code === 'credits_popular' && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="mb-4">
                  <h3 className="text-xl font-bold text-gray-900">{plan.plan_name}</h3>
                  <p className="text-gray-600 text-sm mt-2">{plan.description}</p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline">
                    <span className="text-4xl font-bold text-gray-900">
                      ${plan.price_usd}
                    </span>
                  </div>
                  <div className="text-gray-600 mt-2">
                    <span className="font-semibold text-lg">{plan.credits_amount}</span> sessions
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    ${(plan.price_usd / plan.credits_amount).toFixed(2)} per session
                  </div>
                </div>

                <button
                  onClick={() => handlePurchase(plan.plan_code)}
                  disabled={processingPlan === plan.plan_code}
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
                    plan.plan_code === 'credits_popular'
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-900 text-white hover:bg-gray-800'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {processingPlan === plan.plan_code ? 'Processing...' : 'Buy Now'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* One-Time Features */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            One-Time Purchases
          </h2>
          <p className="text-center text-gray-600 mb-8">
            Unlock powerful features forever
          </p>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {oneTimePurchases.map((plan) => {
              const isOwned =
                (plan.plan_code === 'ai_generator' && userFeatures?.ai_generator_available) ||
                (plan.plan_code === 'qa_management' && userFeatures?.qa_management_available);

              return (
                <div
                  key={plan.id}
                  className="bg-white rounded-lg shadow-md border border-gray-200 p-6 flex flex-col"
                >
                  <div className="mb-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xl font-bold text-gray-900">{plan.plan_name}</h3>
                      {isOwned && (
                        <span className="bg-green-100 text-green-800 text-xs font-semibold px-3 py-1 rounded-full">
                          Owned
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 text-sm mt-2">{plan.description}</p>

                    {/* Show before/after comparison for AI Generator */}
                    {plan.plan_code === 'ai_generator' && (
                      <div className="mt-4 grid grid-cols-2 gap-3">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                          <div className="text-xs font-semibold text-red-600 mb-2">Without AI Generator</div>
                          <div className="text-xs text-red-700 italic">
                            "My strength is [your skill]. At [company], I achieved [metric]..."
                          </div>
                          <div className="text-xs text-red-600 mt-2">❌ Generic placeholders</div>
                        </div>
                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <div className="text-xs font-semibold text-green-600 mb-2">With AI Generator</div>
                          <div className="text-xs text-green-700">
                            "My strength is frontend problem-solving. At Toss, I debugged a 500 error..."
                          </div>
                          <div className="text-xs text-green-600 mt-2">✅ Your real experience</div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mb-6">
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold text-gray-900">
                        ${plan.price_usd}
                      </span>
                      <span className="text-gray-500 ml-2">one-time</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handlePurchase(plan.plan_code)}
                    disabled={isOwned || processingPlan === plan.plan_code}
                    className="w-full py-3 px-6 rounded-lg font-semibold bg-gray-900 text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isOwned
                      ? 'Already Owned'
                      : processingPlan === plan.plan_code
                      ? 'Processing...'
                      : 'Buy Now'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-md border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>

          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">What are interview credits?</h3>
              <p className="text-gray-600">
                Each credit allows you to use our AI assistant during one live video interview
                session. Credits never expire.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">How does billing work?</h3>
              <p className="text-gray-600">
                Pay once, use forever. Credits and features never expire. No recurring charges.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">What payment methods do you accept?</h3>
              <p className="text-gray-600">
                We accept all major credit cards, PayPal, and Apple Pay via Lemon Squeezy.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Can I get a refund?</h3>
              <p className="text-gray-600">
                We offer a 7-day money-back guarantee. Contact support if you're not satisfied.
              </p>
            </div>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-12">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
