'use client';

/**
 * Q&A Pairs Management Page
 * Bulk upload and manage expected interview Q&A pairs
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { useUserFeatures } from '@/hooks/useUserFeatures';

interface QAPair {
    id: string;
    user_id: string;
    question: string;
    answer: string;
    question_type: string;
    source: string;
    usage_count: number;
    last_used_at: string | null;
    created_at: string;
    updated_at: string;
    question_variations?: string[];  // Alternative question phrasings
}

interface ParsedQAPair {
    question: string;
    answer: string;
    question_type: string;
    source: string;
    question_variations?: string[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function QAPairsPage() {
    const router = useRouter();
    const [userId, setUserId] = useState<string | null>(null);

    // Feature gating - check qa_management access
    const { qa_management_available, isLoading: featuresLoading } = useUserFeatures(userId);
    const canEdit = qa_management_available;

    const [qaPairs, setQaPairs] = useState<QAPair[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [editingPair, setEditingPair] = useState<QAPair | null>(null);
    const [isCreating, setIsCreating] = useState(false);

    // Bulk upload state
    const [bulkText, setBulkText] = useState('');
    const [parsedPairs, setParsedPairs] = useState<ParsedQAPair[]>([]);
    const [isParsing, setIsParsing] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [showBulkUpload, setShowBulkUpload] = useState(false);

    // Single Q&A form state
    const [formData, setFormData] = useState({
        question: '',
        answer: '',
        question_type: 'general',
        question_variations: [] as string[],
    });

    // New variation input
    const [newVariation, setNewVariation] = useState('');

    // Check authentication on mount
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

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
            if (!session) {
                router.push('/auth/login');
            } else {
                setUserId(session.user.id);
            }
        });

        return () => subscription.unsubscribe();
    }, [router]);

    // Fetch Q&A pairs when userId is available
    useEffect(() => {
        if (userId) {
            fetchQAPairs();
        }
    }, [userId]);

    const fetchQAPairs = async () => {
        if (!userId) return;

        try {
            setIsLoading(true);
            const response = await fetch(`${API_URL}/api/qa-pairs/${userId}`);
            if (!response.ok) throw new Error('Failed to fetch Q&A pairs');
            const data = await response.json();
            setQaPairs(data || []);
        } catch (err) {
            setError('Failed to load Q&A pairs');
        } finally {
            setIsLoading(false);
        }
    };

    // Parse bulk text with Claude
    const handleParseBulk = async () => {
        if (!bulkText.trim()) {
            setError('Please enter some text to parse');
            return;
        }
        if (!userId) return;

        try {
            setIsParsing(true);
            setError(null);
            const response = await fetch(`${API_URL}/api/qa-pairs/${userId}/bulk-parse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: bulkText }),
            });

            if (!response.ok) throw new Error('Failed to parse Q&A pairs');

            const data = await response.json();
            setParsedPairs(data.parsed_pairs || []);

            if (data.count === 0) {
                setError('No Q&A pairs found in the text. Please check the format.');
            }
        } catch (err) {
            setError('Failed to parse text. Please try again.');
        } finally {
            setIsParsing(false);
        }
    };

    // Upload parsed pairs
    const handleUploadParsed = async () => {
        if (parsedPairs.length === 0 || !userId) return;

        try {
            setIsUploading(true);
            setError(null);
            const response = await fetch(`${API_URL}/api/qa-pairs/${userId}/bulk-upload`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(parsedPairs),
            });

            if (!response.ok) throw new Error('Failed to upload Q&A pairs');

            // Reset and refresh
            setBulkText('');
            setParsedPairs([]);
            setShowBulkUpload(false);
            fetchQAPairs();
        } catch (err) {
            setError('Failed to upload Q&A pairs');
        } finally {
            setIsUploading(false);
        }
    };

    // Create or update single Q&A
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const pairData = {
            question: formData.question,
            answer: formData.answer,
            question_type: formData.question_type,
            source: 'manual',
            question_variations: formData.question_variations,
        };

        try {
            if (editingPair) {
                // Update
                await fetch(`${API_URL}/api/qa-pairs/${editingPair.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(pairData),
                });
            } else {
                // Create
                await fetch(`${API_URL}/api/qa-pairs/${userId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(pairData),
                });
            }

            // Reset and refresh
            resetForm();
            fetchQAPairs();
        } catch (err) {
            setError('Failed to save Q&A pair');
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this Q&A pair?')) return;

        try {
            await fetch(`${API_URL}/api/qa-pairs/${id}`, {
                method: 'DELETE',
            });
            fetchQAPairs();
        } catch (err) {
            setError('Failed to delete Q&A pair');
        }
    };

    const handleEdit = (pair: QAPair) => {
        setEditingPair(pair);
        setFormData({
            question: pair.question,
            answer: pair.answer,
            question_type: pair.question_type,
            question_variations: pair.question_variations || [],
        });
        setIsCreating(true);
        setShowBulkUpload(false);
    };

    const resetForm = () => {
        setFormData({
            question: '',
            answer: '',
            question_type: 'general',
            question_variations: [],
        });
        setNewVariation('');
        setEditingPair(null);
        setIsCreating(false);
    };

    const addVariation = () => {
        if (newVariation.trim() && !formData.question_variations.includes(newVariation.trim())) {
            setFormData({
                ...formData,
                question_variations: [...formData.question_variations, newVariation.trim()],
            });
            setNewVariation('');
        }
    };

    const removeVariation = (index: number) => {
        setFormData({
            ...formData,
            question_variations: formData.question_variations.filter((_, i) => i !== index),
        });
    };

    const getQuestionTypeColor = (type: string) => {
        switch (type) {
            case 'behavioral':
                return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300';
            case 'technical':
                return 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300';
            case 'situational':
                return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300';
            default:
                return 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300';
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
                            Q&A Pairs
                        </h1>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">
                            Upload expected questions for instant answers during practice
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <a
                            href="/interview"
                            className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                        >
                            Interview
                        </a>
                        {!isCreating && !showBulkUpload && (
                            <>
                                <button
                                    onClick={() => {
                                        if (!canEdit) { router.push('/pricing'); return; }
                                        setShowBulkUpload(true);
                                        setIsCreating(false);
                                    }}
                                    className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                >
                                    Bulk Upload
                                </button>
                                <button
                                    onClick={() => {
                                        if (!canEdit) { router.push('/pricing'); return; }
                                        setIsCreating(true);
                                        setShowBulkUpload(false);
                                    }}
                                    className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                                >
                                    Add Q&A
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-4xl px-4 py-6">
                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error}
                        <button
                            onClick={() => setError(null)}
                            className="ml-2 text-sm underline"
                        >
                            Dismiss
                        </button>
                    </div>
                )}

                {/* Bulk Upload Section */}
                {showBulkUpload && (
                    <div className="mb-6 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            Bulk Upload Q&A Pairs
                        </h2>
                        <p className="mb-4 text-sm text-zinc-600 dark:text-zinc-400">
                            Paste your questions and answers in any format. Our AI will parse them automatically.
                        </p>

                        <textarea
                            value={bulkText}
                            onChange={(e) => setBulkText(e.target.value)}
                            placeholder="Example:&#10;Q: Tell me about yourself&#10;A: I'm a software engineer with 5 years of experience...&#10;&#10;Q: What are your strengths?&#10;A: I excel at problem-solving and teamwork..."
                            rows={10}
                            className="w-full rounded-lg border border-zinc-300 px-3 py-2 font-mono text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                        />

                        <div className="mt-4 flex gap-2">
                            <button
                                onClick={handleParseBulk}
                                disabled={isParsing || !bulkText.trim()}
                                className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                            >
                                {isParsing ? 'Parsing...' : 'Parse with AI'}
                            </button>
                            <button
                                onClick={() => {
                                    setShowBulkUpload(false);
                                    setBulkText('');
                                    setParsedPairs([]);
                                }}
                                className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                            >
                                Cancel
                            </button>
                        </div>

                        {/* Parsed results */}
                        {parsedPairs.length > 0 && (
                            <div className="mt-6">
                                <div className="mb-3 flex items-center justify-between">
                                    <h3 className="text-md font-medium text-zinc-900 dark:text-zinc-100">
                                        Parsed {parsedPairs.length} Q&A pairs - Review & Confirm
                                    </h3>
                                    <button
                                        onClick={handleUploadParsed}
                                        disabled={isUploading}
                                        className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
                                    >
                                        {isUploading ? 'Uploading...' : 'Confirm & Upload'}
                                    </button>
                                </div>

                                <div className="space-y-3">
                                    {parsedPairs.map((pair, index) => (
                                        <div
                                            key={index}
                                            className="rounded-lg border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-700 dark:bg-zinc-900"
                                        >
                                            <div className="mb-2 flex items-start justify-between">
                                                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getQuestionTypeColor(pair.question_type)}`}>
                                                    {pair.question_type}
                                                </span>
                                            </div>
                                            <div className="mb-2">
                                                <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Q:</span>
                                                <p className="text-sm text-zinc-900 dark:text-zinc-100">{pair.question}</p>
                                            </div>
                                            <div>
                                                <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">A:</span>
                                                <p className="text-sm text-zinc-600 dark:text-zinc-400">{pair.answer}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Create/Edit Form */}
                {isCreating && (
                    <div className="mb-6 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            {editingPair ? 'Edit Q&A Pair' : 'Add New Q&A Pair'}
                        </h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Question Type
                                </label>
                                <select
                                    value={formData.question_type}
                                    onChange={(e) => setFormData({ ...formData, question_type: e.target.value })}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                >
                                    <option value="general">General</option>
                                    <option value="behavioral">Behavioral</option>
                                    <option value="technical">Technical</option>
                                    <option value="situational">Situational</option>
                                </select>
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Question
                                </label>
                                <textarea
                                    value={formData.question}
                                    onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                                    placeholder="e.g., Tell me about a time when you faced a difficult challenge"
                                    rows={3}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Answer
                                </label>
                                <textarea
                                    value={formData.answer}
                                    onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                                    placeholder="Your prepared answer..."
                                    rows={6}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Question Variations (Optional)
                                </label>
                                <p className="mb-2 text-xs text-zinc-500 dark:text-zinc-400">
                                    Add alternative phrasings to improve matching (e.g., "What if CTO wants Claude?" for "CTO says they'll use Claude")
                                </p>

                                {formData.question_variations.length > 0 && (
                                    <div className="mb-2 flex flex-wrap gap-2">
                                        {formData.question_variations.map((variation, index) => (
                                            <span
                                                key={index}
                                                className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                                            >
                                                {variation}
                                                <button
                                                    type="button"
                                                    onClick={() => removeVariation(index)}
                                                    className="ml-1 hover:text-blue-900 dark:hover:text-blue-100"
                                                >
                                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </button>
                                            </span>
                                        ))}
                                    </div>
                                )}

                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={newVariation}
                                        onChange={(e) => setNewVariation(e.target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter') {
                                                e.preventDefault();
                                                addVariation();
                                            }
                                        }}
                                        placeholder="Enter alternative question phrasing..."
                                        className="flex-1 rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    />
                                    <button
                                        type="button"
                                        onClick={addVariation}
                                        className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                    >
                                        Add
                                    </button>
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    type="submit"
                                    className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                                >
                                    {editingPair ? 'Update' : 'Create'}
                                </button>
                                <button
                                    type="button"
                                    onClick={resetForm}
                                    className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                )}

                {/* Q&A Pairs list */}
                {qaPairs.length === 0 ? (
                    <div className="rounded-lg border border-zinc-200 bg-white p-8 text-center dark:border-zinc-800 dark:bg-zinc-950">
                        <p className="text-zinc-500 dark:text-zinc-400">
                            No Q&A pairs yet. Upload your expected interview questions for instant answers during practice.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {qaPairs.map((pair) => (
                            <div
                                key={pair.id}
                                className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
                            >
                                <div className="mb-3 flex items-start justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getQuestionTypeColor(pair.question_type)}`}>
                                            {pair.question_type}
                                        </span>
                                        <span className="text-xs text-zinc-500 dark:text-zinc-400">
                                            Used {pair.usage_count} times
                                        </span>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => {
                                                if (!canEdit) { router.push('/pricing'); return; }
                                                handleEdit(pair);
                                            }}
                                            className="text-sm text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => {
                                                if (!canEdit) { router.push('/pricing'); return; }
                                                handleDelete(pair.id);
                                            }}
                                            className="text-sm text-red-500 hover:text-red-700"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <div>
                                        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Question:</span>
                                        <p className="text-sm text-zinc-900 dark:text-zinc-100">{pair.question}</p>
                                    </div>
                                    <div>
                                        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Answer:</span>
                                        <p className="text-sm text-zinc-600 dark:text-zinc-400">{pair.answer}</p>
                                    </div>
                                </div>

                                {pair.last_used_at && (
                                    <div className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
                                        Last used: {new Date(pair.last_used_at).toLocaleDateString()}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
