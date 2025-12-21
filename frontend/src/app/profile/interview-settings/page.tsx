'use client';

/**
 * Interview Profile Settings Page
 * Allows users to customize their interview persona and answer style
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const ANSWER_STYLES = [
    { value: 'concise', label: 'Concise', description: 'Brief, direct answers (20-30 words)' },
    { value: 'balanced', label: 'Balanced', description: 'Moderate detail (30-60 words)' },
    { value: 'detailed', label: 'Detailed', description: 'Comprehensive answers (60-100 words)' },
];

export default function InterviewSettingsPage() {
    const router = useRouter();
    const [userId, setUserId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [hasProfile, setHasProfile] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        full_name: '',
        target_role: '',
        target_company: '',
        projects_summary: '',
        answer_style: 'balanced' as 'concise' | 'balanced' | 'detailed',
        technical_stack: '',  // Comma-separated
        key_strengths: '',     // Comma-separated
    });

    // Check authentication
    useEffect(() => {
        const checkAuth = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push('/auth/login');
                return;
            }
            setUserId(session.user.id);
        };
        checkAuth();

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            if (!session) {
                router.push('/auth/login');
            } else {
                setUserId(session.user.id);
            }
        });

        return () => subscription.unsubscribe();
    }, [router]);

    // Load existing profile
    useEffect(() => {
        if (!userId) return;

        const loadProfile = async () => {
            try {
                setIsLoading(true);
                const response = await fetch(`${API_URL}/api/interview-profile/${userId}`);
                const data = await response.json();

                if (data.has_profile && data.profile) {
                    const profile = data.profile;
                    setFormData({
                        full_name: profile.full_name || '',
                        target_role: profile.target_role || '',
                        target_company: profile.target_company || '',
                        projects_summary: profile.projects_summary || '',
                        answer_style: profile.answer_style || 'balanced',
                        technical_stack: (profile.technical_stack || []).join(', '),
                        key_strengths: (profile.key_strengths || []).join(', '),
                    });
                    setHasProfile(true);
                }
            } catch (err) {
                console.error('Failed to load profile:', err);
                setError('Failed to load your profile');
            } finally {
                setIsLoading(false);
            }
        };

        loadProfile();
    }, [userId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userId) return;

        setIsSaving(true);
        setError(null);
        setSuccessMessage(null);

        try {
            const profileData = {
                full_name: formData.full_name || null,
                target_role: formData.target_role || null,
                target_company: formData.target_company || null,
                projects_summary: formData.projects_summary || null,
                answer_style: formData.answer_style,
                technical_stack: formData.technical_stack
                    ? formData.technical_stack.split(',').map(s => s.trim()).filter(Boolean)
                    : [],
                key_strengths: formData.key_strengths
                    ? formData.key_strengths.split(',').map(s => s.trim()).filter(Boolean)
                    : [],
            };

            const method = hasProfile ? 'PUT' : 'POST';
            const response = await fetch(`${API_URL}/api/interview-profile/${userId}`, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profileData),
            });

            if (!response.ok) {
                throw new Error('Failed to save profile');
            }

            setSuccessMessage('Profile saved successfully!');
            setHasProfile(true);

            // Clear success message after 3 seconds
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err) {
            console.error('Failed to save profile:', err);
            setError('Failed to save profile. Please try again.');
        } finally {
            setIsSaving(false);
        }
    };

    if (!userId || isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
                <div className="text-zinc-500">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            {/* Header */}
            <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
                    <div>
                        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
                            Interview Settings
                        </h1>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">
                            Customize how the AI generates your interview answers
                        </p>
                    </div>
                    <a
                        href="/interview"
                        className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                    >
                        Back to Interview
                    </a>
                </div>
            </header>

            <main className="mx-auto max-w-4xl px-4 py-6">
                {/* Messages */}
                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error}
                    </div>
                )}

                {successMessage && (
                    <div className="mb-4 rounded-lg bg-green-50 p-4 text-green-700 dark:bg-green-950 dark:text-green-300">
                        {successMessage}
                    </div>
                )}

                {/* Info Banner */}
                <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
                    <h3 className="mb-2 font-medium text-blue-900 dark:text-blue-100">
                        💡 Why customize your profile?
                    </h3>
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                        The AI will use this information to generate personalized, authentic answers
                        that sound like YOU. The more details you provide, the better your answers will be!
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Basic Information */}
                    <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            Basic Information
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Your Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    placeholder="e.g., Alex Kim"
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                />
                            </div>

                            <div className="grid gap-4 md:grid-cols-2">
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                        Target Role
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.target_role}
                                        onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                                        placeholder="e.g., Software Engineer"
                                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                        Target Company
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.target_company}
                                        onChange={(e) => setFormData({ ...formData, target_company: e.target.value })}
                                        placeholder="e.g., Google"
                                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Background */}
                    <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            Your Background
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Projects & Experience Summary
                                </label>
                                <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                                    Describe your key projects, achievements, and metrics. The AI will reference these when answering questions.
                                </p>
                                <textarea
                                    value={formData.projects_summary}
                                    onChange={(e) => setFormData({ ...formData, projects_summary: e.target.value })}
                                    placeholder="Example:&#10;&#10;**E-commerce Platform (2023-2024)**&#10;- Built real-time inventory system serving 100K+ daily users&#10;- Reduced page load time by 40% through React optimization&#10;- Led team of 3 engineers&#10;&#10;**AI Chatbot Project (2024)**&#10;- Implemented RAG system reducing hallucinations by 60%&#10;- Saved $2K/month by optimizing LLM calls"
                                    rows={10}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 font-mono text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Technical Stack (comma-separated)
                                </label>
                                <input
                                    type="text"
                                    value={formData.technical_stack}
                                    onChange={(e) => setFormData({ ...formData, technical_stack: e.target.value })}
                                    placeholder="e.g., React, Python, PostgreSQL, AWS, Docker"
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Key Strengths (comma-separated)
                                </label>
                                <input
                                    type="text"
                                    value={formData.key_strengths}
                                    onChange={(e) => setFormData({ ...formData, key_strengths: e.target.value })}
                                    placeholder="e.g., System design, Team leadership, Cost optimization"
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Communication Style */}
                    <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            Communication Style
                        </h2>

                        <div className="space-y-3">
                            {ANSWER_STYLES.map((style) => (
                                <label
                                    key={style.value}
                                    className={`flex cursor-pointer items-start gap-3 rounded-lg border p-4 transition-colors ${
                                        formData.answer_style === style.value
                                            ? 'border-zinc-900 bg-zinc-50 dark:border-zinc-100 dark:bg-zinc-800'
                                            : 'border-zinc-200 hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-900'
                                    }`}
                                >
                                    <input
                                        type="radio"
                                        name="answer_style"
                                        value={style.value}
                                        checked={formData.answer_style === style.value}
                                        onChange={(e) => setFormData({ ...formData, answer_style: e.target.value as typeof formData.answer_style })}
                                        className="mt-1"
                                    />
                                    <div>
                                        <div className="font-medium text-zinc-900 dark:text-zinc-100">
                                            {style.label}
                                        </div>
                                        <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                            {style.description}
                                        </div>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Save Button */}
                    <div className="flex gap-3">
                        <button
                            type="submit"
                            disabled={isSaving}
                            className="rounded-lg bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                        >
                            {isSaving ? 'Saving...' : hasProfile ? 'Update Profile' : 'Create Profile'}
                        </button>
                        <a
                            href="/interview"
                            className="rounded-lg border border-zinc-300 px-6 py-3 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                        >
                            Cancel
                        </a>
                    </div>
                </form>
            </main>
        </div>
    );
}
