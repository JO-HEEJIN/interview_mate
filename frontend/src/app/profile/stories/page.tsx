'use client';

/**
 * STAR Stories Management Page
 */

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

interface StarStory {
    id: string;
    title: string;
    situation: string;
    task: string;
    action: string;
    result: string;
    tags: string[];
    is_favorite: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function StarStoriesPage() {
    const { data: session, status } = useSession();
    const router = useRouter();
    const [stories, setStories] = useState<StarStory[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [editingStory, setEditingStory] = useState<StarStory | null>(null);
    const [isCreating, setIsCreating] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        title: '',
        situation: '',
        task: '',
        action: '',
        result: '',
        tags: '',
    });

    // Redirect if not authenticated
    useEffect(() => {
        if (status === 'unauthenticated') {
            router.push('/auth/login');
        }
    }, [status, router]);

    // Fetch stories
    useEffect(() => {
        if (session?.user?.id) {
            fetchStories();
        }
    }, [session]);

    const fetchStories = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`${API_URL}/api/profile/star-stories/${session?.user?.id}`);
            const data = await response.json();
            setStories(data.stories || []);
        } catch (err) {
            setError('Failed to load stories');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const storyData = {
            title: formData.title,
            situation: formData.situation,
            task: formData.task,
            action: formData.action,
            result: formData.result,
            tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
        };

        try {
            if (editingStory) {
                // Update
                await fetch(`${API_URL}/api/profile/star-stories/${editingStory.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(storyData),
                });
            } else {
                // Create
                await fetch(`${API_URL}/api/profile/star-stories/${session?.user?.id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(storyData),
                });
            }

            // Reset and refresh
            resetForm();
            fetchStories();
        } catch (err) {
            setError('Failed to save story');
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this story?')) return;

        try {
            await fetch(`${API_URL}/api/profile/star-stories/${id}`, {
                method: 'DELETE',
            });
            fetchStories();
        } catch (err) {
            setError('Failed to delete story');
        }
    };

    const handleEdit = (story: StarStory) => {
        setEditingStory(story);
        setFormData({
            title: story.title,
            situation: story.situation,
            task: story.task,
            action: story.action,
            result: story.result,
            tags: story.tags.join(', '),
        });
        setIsCreating(true);
    };

    const resetForm = () => {
        setFormData({
            title: '',
            situation: '',
            task: '',
            action: '',
            result: '',
            tags: '',
        });
        setEditingStory(null);
        setIsCreating(false);
    };

    if (status === 'loading' || isLoading) {
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
                            STAR Stories
                        </h1>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">
                            Manage your experience stories for interview answers
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <a
                            href="/interview"
                            className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                        >
                            Interview
                        </a>
                        {!isCreating && (
                            <button
                                onClick={() => setIsCreating(true)}
                                className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                            >
                                Add Story
                            </button>
                        )}
                    </div>
                </div>
            </header>

            <main className="mx-auto max-w-4xl px-4 py-6">
                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700 dark:bg-red-950 dark:text-red-300">
                        {error}
                    </div>
                )}

                {/* Create/Edit Form */}
                {isCreating && (
                    <div className="mb-6 rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
                        <h2 className="mb-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">
                            {editingStory ? 'Edit Story' : 'Add New Story'}
                        </h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Title
                                </label>
                                <input
                                    type="text"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    placeholder="e.g., Led cross-functional project at Company X"
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Situation
                                </label>
                                <textarea
                                    value={formData.situation}
                                    onChange={(e) => setFormData({ ...formData, situation: e.target.value })}
                                    placeholder="Describe the context and background..."
                                    rows={3}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Task
                                </label>
                                <textarea
                                    value={formData.task}
                                    onChange={(e) => setFormData({ ...formData, task: e.target.value })}
                                    placeholder="What was your specific responsibility?"
                                    rows={2}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Action
                                </label>
                                <textarea
                                    value={formData.action}
                                    onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                                    placeholder="What actions did you take?"
                                    rows={3}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Result
                                </label>
                                <textarea
                                    value={formData.result}
                                    onChange={(e) => setFormData({ ...formData, result: e.target.value })}
                                    placeholder="What was the outcome? Include metrics if possible."
                                    rows={2}
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                                    Tags (comma-separated)
                                </label>
                                <input
                                    type="text"
                                    value={formData.tags}
                                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                                    placeholder="e.g., leadership, problem-solving, teamwork"
                                    className="w-full rounded-lg border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                                />
                            </div>

                            <div className="flex gap-2">
                                <button
                                    type="submit"
                                    className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                                >
                                    {editingStory ? 'Update' : 'Create'}
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

                {/* Stories list */}
                {stories.length === 0 ? (
                    <div className="rounded-lg border border-zinc-200 bg-white p-8 text-center dark:border-zinc-800 dark:bg-zinc-950">
                        <p className="text-zinc-500 dark:text-zinc-400">
                            No stories yet. Add your first STAR story to enhance your interview answers.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {stories.map((story) => (
                            <div
                                key={story.id}
                                className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
                            >
                                <div className="mb-3 flex items-start justify-between">
                                    <h3 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                                        {story.title}
                                    </h3>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleEdit(story)}
                                            className="text-sm text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDelete(story.id)}
                                            className="text-sm text-red-500 hover:text-red-700"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>

                                <div className="space-y-2 text-sm">
                                    <div>
                                        <span className="font-medium text-zinc-700 dark:text-zinc-300">S: </span>
                                        <span className="text-zinc-600 dark:text-zinc-400">{story.situation}</span>
                                    </div>
                                    <div>
                                        <span className="font-medium text-zinc-700 dark:text-zinc-300">T: </span>
                                        <span className="text-zinc-600 dark:text-zinc-400">{story.task}</span>
                                    </div>
                                    <div>
                                        <span className="font-medium text-zinc-700 dark:text-zinc-300">A: </span>
                                        <span className="text-zinc-600 dark:text-zinc-400">{story.action}</span>
                                    </div>
                                    <div>
                                        <span className="font-medium text-zinc-700 dark:text-zinc-300">R: </span>
                                        <span className="text-zinc-600 dark:text-zinc-400">{story.result}</span>
                                    </div>
                                </div>

                                {story.tags.length > 0 && (
                                    <div className="mt-3 flex flex-wrap gap-1">
                                        {story.tags.map((tag, i) => (
                                            <span
                                                key={i}
                                                className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                                            >
                                                {tag}
                                            </span>
                                        ))}
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
