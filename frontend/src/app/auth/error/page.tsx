'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

function AuthErrorContent() {
    const searchParams = useSearchParams();
    const error = searchParams.get('error');

    const getErrorMessage = (error: string | null) => {
        switch (error) {
            case 'Configuration':
                return 'There is a problem with the server configuration.';
            case 'AccessDenied':
                return 'Access denied. You do not have permission to sign in.';
            case 'Verification':
                return 'The verification link has expired or has already been used.';
            case 'OAuthSignin':
                return 'Error occurred while signing in with the OAuth provider.';
            case 'OAuthCallback':
                return 'Error occurred while processing the OAuth callback.';
            case 'OAuthCreateAccount':
                return 'Could not create an OAuth account.';
            case 'EmailCreateAccount':
                return 'Could not create an email account.';
            case 'Callback':
                return 'Error occurred during the callback.';
            case 'OAuthAccountNotLinked':
                return 'This email is already associated with another account.';
            case 'EmailSignin':
                return 'Error sending the verification email.';
            case 'CredentialsSignin':
                return 'Invalid email or password.';
            case 'SessionRequired':
                return 'Please sign in to access this page.';
            default:
                return 'An unexpected error occurred.';
        }
    };

    return (
        <div className="max-w-md w-full space-y-8 text-center">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">InterviewMate.ai</h1>
                <h2 className="mt-6 text-2xl font-semibold text-red-600">
                    Authentication Error
                </h2>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <p className="text-red-700">{getErrorMessage(error)}</p>
            </div>

            <div className="space-y-4">
                <Link
                    href="/auth/login"
                    className="block w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                    Try again
                </Link>
                <Link
                    href="/"
                    className="block w-full py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                    Go to homepage
                </Link>
            </div>
        </div>
    );
}

export default function AuthErrorPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <Suspense fallback={<div>Loading...</div>}>
                <AuthErrorContent />
            </Suspense>
        </div>
    );
}
