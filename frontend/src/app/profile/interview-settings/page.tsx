'use client';

/**
 * Interview Profile Settings Page
 * Allows users to customize their interview persona and answer style
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useProfile } from '@/contexts/ProfileContext';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const ANSWER_STYLES = [
    { value: 'concise', label: 'Concise', description: 'Brief, direct answers (20-30 words)' },
    { value: 'balanced', label: 'Balanced', description: 'Moderate detail (30-60 words)' },
    { value: 'detailed', label: 'Detailed', description: 'Comprehensive answers (60-100 words)' },
];

export default function InterviewSettingsPage() {
    const router = useRouter();
    const [userId, setUserId] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

    // Profile context
    const { activeProfile, isLoading: profileLoading, updateProfile, createProfile } = useProfile();

    // Auto-save timer ref
    const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
    const isInitialLoadRef = useRef(true);

    // Form state
    const [formData, setFormData] = useState({
        full_name: '',
        target_role: '',
        target_company: '',
        projects_summary: '',
        answer_style: 'balanced' as 'concise' | 'balanced' | 'detailed',
        technical_stack: '',  // Comma-separated
        key_strengths: '',     // Comma-separated
        custom_instructions: '',  // User-specific answer generation rules
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

    // Sync form data with active profile
    useEffect(() => {
        if (activeProfile) {
            isInitialLoadRef.current = true;
            setFormData({
                full_name: activeProfile.full_name || '',
                target_role: activeProfile.target_role || '',
                target_company: activeProfile.target_company || '',
                projects_summary: activeProfile.projects_summary || '',
                answer_style: activeProfile.answer_style || 'balanced',
                technical_stack: (activeProfile.technical_stack || []).join(', '),
                key_strengths: (activeProfile.key_strengths || []).join(', '),
                custom_instructions: activeProfile.custom_instructions || '',
            });
            // Reset initial load flag after a short delay
            setTimeout(() => {
                isInitialLoadRef.current = false;
            }, 100);
        }
    }, [activeProfile]);

    // Auto-save function
    const performAutoSave = useCallback(async (data: typeof formData) => {
        if (!activeProfile) return;

        setAutoSaveStatus('saving');

        const profileData = {
            full_name: data.full_name || undefined,
            target_role: data.target_role || undefined,
            target_company: data.target_company || undefined,
            projects_summary: data.projects_summary || undefined,
            answer_style: data.answer_style,
            technical_stack: data.technical_stack
                ? data.technical_stack.split(',').map(s => s.trim()).filter(Boolean)
                : [],
            key_strengths: data.key_strengths
                ? data.key_strengths.split(',').map(s => s.trim()).filter(Boolean)
                : [],
            custom_instructions: data.custom_instructions || undefined,
        };

        const result = await updateProfile(activeProfile.id, profileData);

        if (result) {
            setAutoSaveStatus('saved');
            setTimeout(() => setAutoSaveStatus('idle'), 2000);
        } else {
            setAutoSaveStatus('idle');
        }
    }, [activeProfile, updateProfile]);

    // Trigger auto-save when form data changes
    useEffect(() => {
        // Skip auto-save on initial load
        if (isInitialLoadRef.current) return;
        if (!activeProfile) return;

        // Clear existing timer
        if (autoSaveTimerRef.current) {
            clearTimeout(autoSaveTimerRef.current);
        }

        // Set new timer for auto-save (1.5 seconds after last change)
        autoSaveTimerRef.current = setTimeout(() => {
            performAutoSave(formData);
        }, 1500);

        return () => {
            if (autoSaveTimerRef.current) {
                clearTimeout(autoSaveTimerRef.current);
            }
        };
    }, [formData, activeProfile, performAutoSave]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!activeProfile) return;

        setIsSaving(true);
        setError(null);
        setSuccessMessage(null);

        try {
            const profileData = {
                full_name: formData.full_name || undefined,
                target_role: formData.target_role || undefined,
                target_company: formData.target_company || undefined,
                projects_summary: formData.projects_summary || undefined,
                answer_style: formData.answer_style,
                technical_stack: formData.technical_stack
                    ? formData.technical_stack.split(',').map(s => s.trim()).filter(Boolean)
                    : [],
                key_strengths: formData.key_strengths
                    ? formData.key_strengths.split(',').map(s => s.trim()).filter(Boolean)
                    : [],
                custom_instructions: formData.custom_instructions || undefined,
            };

            const result = await updateProfile(activeProfile.id, profileData);

            if (result) {
                setSuccessMessage('Profile saved successfully!');
                // Clear success message after 3 seconds
                setTimeout(() => setSuccessMessage(null), 3000);
            } else {
                throw new Error('Failed to save profile');
            }
        } catch (err) {
            console.error('Failed to save profile:', err);
            setError('Failed to save profile. Please try again.');
        } finally {
            setIsSaving(false);
        }
    };

    if (!userId || profileLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
                <div className="text-zinc-500">Loading...</div>
            </div>
        );
    }

    // Show message if no profile is selected
    if (!activeProfile) {
        return (
            <div className="min-h-screen bg-zinc-50 dark:bg-black">
                <div className="mx-auto max-w-4xl px-4 py-6">
                    <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 dark:border-amber-800 dark:bg-amber-950">
                        <h2 className="text-lg font-semibold text-amber-900 dark:text-amber-100">
                            No Profile Selected
                        </h2>
                        <p className="mt-2 text-amber-700 dark:text-amber-300">
                            Please create or select a profile to customize interview settings.
                        </p>
                        <button
                            onClick={() => router.push('/profile/manage')}
                            className="mt-4 rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700"
                        >
                            Manage Profiles
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            {/* Header */}
            <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
                <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
                    <div>
                        {/* Profile Indicator + Auto-save Status */}
                        <div className="mb-2 flex items-center gap-2">
                            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-bold text-white">
                                {activeProfile.profile_name.charAt(0).toUpperCase()}
                            </div>
                            <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                                {activeProfile.profile_name}
                            </span>
                            {autoSaveStatus === 'saving' && (
                                <span className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400">
                                    <svg className="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Saving...
                                </span>
                            )}
                            {autoSaveStatus === 'saved' && (
                                <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    Saved
                                </span>
                            )}
                        </div>
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
                                        Target Position/Goal
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.target_role}
                                        onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                                        placeholder="e.g., Software Engineer, PhD Candidate, F1 Visa, MBA Applicant"
                                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                        Target Organization
                                    </label>
                                    <input
                                        type="text"
                                        value={formData.target_company}
                                        onChange={(e) => setFormData({ ...formData, target_company: e.target.value })}
                                        placeholder="e.g., Google, MIT, US Embassy, Stanford MBA"
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
                                    Background Summary
                                </label>
                                <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                                    Describe your key achievements, projects, research, or experiences. The AI will reference these when answering questions.
                                </p>
                                <textarea
                                    value={formData.projects_summary}
                                    onChange={(e) => setFormData({ ...formData, projects_summary: e.target.value })}
                                    placeholder="Examples:&#10;&#10;For Job Interviews:&#10;- Built real-time inventory system serving 100K+ daily users&#10;- Led team of 3 engineers&#10;&#10;For PhD Defense:&#10;- Research on neural network optimization&#10;- Published 3 papers in top-tier conferences&#10;&#10;For Visa Interview:&#10;- Accepted to Stanford CS PhD program&#10;- Research funding secured for 4 years&#10;&#10;For School Admissions:&#10;- Founded startup with $50K revenue&#10;- Led community service initiative"
                                    rows={10}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 font-mono text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Skills & Expertise (comma-separated)
                                </label>
                                <input
                                    type="text"
                                    value={formData.technical_stack}
                                    onChange={(e) => setFormData({ ...formData, technical_stack: e.target.value })}
                                    placeholder="e.g., React, Machine Learning, Research Methods, Data Analysis"
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
                                    placeholder="e.g., Problem solving, Leadership, Research, Communication"
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

                    {/* Custom Instructions */}
                    <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            Custom Interview Instructions (Advanced)
                        </h2>

                        <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
                            <h3 className="mb-2 font-medium text-blue-900 dark:text-blue-100">
                                What are Custom Instructions?
                            </h3>
                            <p className="text-sm text-blue-800 dark:text-blue-200">
                                Add specific rules for how AI should generate answers for YOUR interviews.
                                This makes the system work for any role, not just generic advice.
                            </p>
                            <ul className="mt-2 space-y-1 text-sm text-blue-800 dark:text-blue-200">
                                <li>- Answer style (e.g., "Be concise and confident, avoid filler words")</li>
                                <li>- Domain context (e.g., "For PhD defense, emphasize methodology rigor")</li>
                                <li>- Cultural notes (e.g., "For visa interview, keep answers brief and factual")</li>
                                <li>- Personal preferences (e.g., "Always mention my leadership experience")</li>
                            </ul>
                        </div>

                        <div>
                            <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                Your Custom Instructions
                            </label>
                            <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                                These instructions are appended to the base system prompt. Leave blank to use default behavior.
                            </p>
                            <textarea
                                value={formData.custom_instructions}
                                onChange={(e) => setFormData({ ...formData, custom_instructions: e.target.value })}
                                placeholder={"Examples:\n\nFor Job Interviews:\n- Use STAR format for behavioral questions\n- Emphasize quantifiable results\n\nFor PhD Defense:\n- Be prepared to defend methodology choices\n- Reference specific papers when relevant\n\nFor Visa Interviews:\n- Keep answers short (1-2 sentences)\n- Focus on ties to home country\n\nFor School Admissions:\n- Show genuine interest in the program\n- Connect experiences to future goals"}
                                rows={15}
                                className="w-full rounded-lg border border-zinc-300 px-3 py-2 font-mono text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                            />
                        </div>
                    </div>

                    {/* Save Button */}
                    <div className="flex gap-3">
                        <button
                            type="submit"
                            disabled={isSaving}
                            className="rounded-lg bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                        >
                            {isSaving ? 'Saving...' : 'Save Profile'}
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
