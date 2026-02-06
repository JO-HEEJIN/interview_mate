'use client';

/**
 * Profile Management Page
 * Allows users to view, create, edit, duplicate, and delete interview profiles
 */

import { useState } from 'react';
import { useProfile, Profile } from '@/contexts/ProfileContext';
import Link from 'next/link';

export default function ProfileManagePage() {
    const {
        profiles,
        activeProfile,
        isLoading,
        error,
        switchProfile,
        createProfile,
        updateProfile,
        deleteProfile,
        duplicateProfile,
        setDefaultProfile,
    } = useProfile();

    const [editingProfile, setEditingProfile] = useState<string | null>(null);
    const [editName, setEditName] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [newProfileName, setNewProfileName] = useState('');
    const [actionError, setActionError] = useState<string | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

    // Handle profile name edit
    const handleEdit = (profile: Profile) => {
        setEditingProfile(profile.id);
        setEditName(profile.profile_name);
        setActionError(null);
    };

    const handleSaveEdit = async (profileId: string) => {
        if (!editName.trim()) {
            setActionError('Profile name cannot be empty');
            return;
        }

        const result = await updateProfile(profileId, { profile_name: editName.trim() });
        if (result) {
            setEditingProfile(null);
            setEditName('');
            setActionError(null);
        } else {
            setActionError('Failed to update profile name');
        }
    };

    const handleCancelEdit = () => {
        setEditingProfile(null);
        setEditName('');
        setActionError(null);
    };

    // Handle profile creation
    const handleCreate = async () => {
        if (!newProfileName.trim()) {
            setActionError('Profile name is required');
            return;
        }

        const result = await createProfile(newProfileName.trim());
        if (result) {
            setNewProfileName('');
            setIsCreating(false);
            setActionError(null);
        } else {
            setActionError('Failed to create profile');
        }
    };

    // Handle profile duplication
    const handleDuplicate = async (profile: Profile) => {
        const newName = `${profile.profile_name} (Copy)`;
        const result = await duplicateProfile(profile.id, newName);
        if (!result) {
            setActionError('Failed to duplicate profile');
        }
    };

    // Handle profile deletion
    const handleDelete = async (profileId: string) => {
        const result = await deleteProfile(profileId);
        if (result) {
            setDeleteConfirm(null);
        } else {
            setActionError('Failed to delete profile');
        }
    };

    // Handle set default
    const handleSetDefault = async (profileId: string) => {
        await setDefaultProfile(profileId);
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 py-12">
                <div className="mx-auto max-w-4xl px-4">
                    <div className="flex items-center justify-center py-20">
                        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900 py-12">
            <div className="mx-auto max-w-4xl px-4">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">
                        Manage Profiles
                    </h1>
                    <p className="mt-2 text-zinc-600 dark:text-zinc-400">
                        Create and manage interview profiles for different applications (e.g., Google SWE, MIT PhD, F1 Visa)
                    </p>
                </div>

                {/* Error Message */}
                {(error || actionError) && (
                    <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 dark:bg-red-950 dark:border-red-800">
                        <p className="text-sm text-red-700 dark:text-red-300">{error || actionError}</p>
                    </div>
                )}

                {/* Create New Profile */}
                {isCreating ? (
                    <div className="mb-6 rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-700 dark:bg-zinc-800">
                        <h3 className="mb-4 font-semibold text-zinc-900 dark:text-zinc-100">Create New Profile</h3>
                        <input
                            type="text"
                            value={newProfileName}
                            onChange={(e) => setNewProfileName(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleCreate();
                                if (e.key === 'Escape') {
                                    setIsCreating(false);
                                    setNewProfileName('');
                                }
                            }}
                            placeholder="Profile name (e.g., Google SWE, MIT PhD)"
                            className="w-full rounded-lg border border-zinc-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-700 dark:text-zinc-100"
                            autoFocus
                        />
                        <div className="mt-4 flex gap-2">
                            <button
                                onClick={handleCreate}
                                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                            >
                                Create Profile
                            </button>
                            <button
                                onClick={() => {
                                    setIsCreating(false);
                                    setNewProfileName('');
                                    setActionError(null);
                                }}
                                className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-700"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <button
                        onClick={() => setIsCreating(true)}
                        className="mb-6 flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-zinc-300 bg-white py-6 text-zinc-600 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:border-blue-500 dark:hover:bg-blue-950 dark:hover:text-blue-400"
                    >
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Create New Profile
                    </button>
                )}

                {/* Profile List */}
                <div className="space-y-4">
                    {profiles.length === 0 ? (
                        <div className="rounded-xl border border-zinc-200 bg-white p-12 text-center dark:border-zinc-700 dark:bg-zinc-800">
                            <svg className="mx-auto h-12 w-12 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            <h3 className="mt-4 text-lg font-medium text-zinc-900 dark:text-zinc-100">No profiles yet</h3>
                            <p className="mt-2 text-zinc-500 dark:text-zinc-400">
                                Create your first profile to start preparing for interviews
                            </p>
                        </div>
                    ) : (
                        profiles.map((profile) => (
                            <div
                                key={profile.id}
                                className={`rounded-xl border bg-white p-6 transition-all dark:bg-zinc-800 ${
                                    activeProfile?.id === profile.id
                                        ? 'border-blue-400 ring-2 ring-blue-100 dark:border-blue-500 dark:ring-blue-900'
                                        : 'border-zinc-200 dark:border-zinc-700'
                                }`}
                            >
                                {/* Delete Confirmation */}
                                {deleteConfirm === profile.id ? (
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="font-medium text-red-600 dark:text-red-400">
                                                Delete "{profile.profile_name}"?
                                            </p>
                                            <p className="text-sm text-zinc-500 dark:text-zinc-400">
                                                This will also delete all contexts, Q&A pairs, and stories in this profile.
                                            </p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleDelete(profile.id)}
                                                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
                                            >
                                                Delete
                                            </button>
                                            <button
                                                onClick={() => setDeleteConfirm(null)}
                                                className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-700"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : editingProfile === profile.id ? (
                                    /* Edit Mode */
                                    <div className="flex items-center gap-4">
                                        <input
                                            type="text"
                                            value={editName}
                                            onChange={(e) => setEditName(e.target.value)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') handleSaveEdit(profile.id);
                                                if (e.key === 'Escape') handleCancelEdit();
                                            }}
                                            className="flex-1 rounded-lg border border-zinc-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-700 dark:text-zinc-100"
                                            autoFocus
                                        />
                                        <button
                                            onClick={() => handleSaveEdit(profile.id)}
                                            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                                        >
                                            Save
                                        </button>
                                        <button
                                            onClick={handleCancelEdit}
                                            className="rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-700"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                ) : (
                                    /* Normal Mode */
                                    <>
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-4">
                                                {/* Profile Avatar */}
                                                <div className={`flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full text-lg font-bold text-white ${
                                                    activeProfile?.id === profile.id
                                                        ? 'bg-gradient-to-br from-blue-500 to-purple-600'
                                                        : 'bg-zinc-400 dark:bg-zinc-600'
                                                }`}>
                                                    {profile.profile_name.charAt(0).toUpperCase()}
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
                                                            {profile.profile_name}
                                                        </h3>
                                                        {profile.is_default && (
                                                            <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                                                                Default
                                                            </span>
                                                        )}
                                                        {activeProfile?.id === profile.id && (
                                                            <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                                                                Active
                                                            </span>
                                                        )}
                                                    </div>
                                                    {(profile.target_role || profile.target_company) && (
                                                        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
                                                            {profile.target_role}
                                                            {profile.target_role && profile.target_company && ' @ '}
                                                            {profile.target_company}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Action Buttons */}
                                            <div className="flex items-center gap-2">
                                                {activeProfile?.id !== profile.id && (
                                                    <button
                                                        onClick={() => switchProfile(profile.id)}
                                                        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                                                    >
                                                        Switch to
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => handleEdit(profile)}
                                                    className="rounded-lg border border-zinc-300 p-2 text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-700"
                                                    title="Rename"
                                                >
                                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                    </svg>
                                                </button>
                                                <button
                                                    onClick={() => handleDuplicate(profile)}
                                                    className="rounded-lg border border-zinc-300 p-2 text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-700"
                                                    title="Duplicate"
                                                >
                                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                                    </svg>
                                                </button>
                                                {!profile.is_default && (
                                                    <button
                                                        onClick={() => handleSetDefault(profile.id)}
                                                        className="rounded-lg border border-zinc-300 p-2 text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-700"
                                                        title="Set as default"
                                                    >
                                                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                                                        </svg>
                                                    </button>
                                                )}
                                                {profiles.length > 1 && (
                                                    <button
                                                        onClick={() => setDeleteConfirm(profile.id)}
                                                        className="rounded-lg border border-red-300 p-2 text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950"
                                                        title="Delete"
                                                    >
                                                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                        </svg>
                                                    </button>
                                                )}
                                            </div>
                                        </div>

                                        {/* Quick Links */}
                                        <div className="mt-4 flex flex-wrap gap-2 border-t border-zinc-100 pt-4 dark:border-zinc-700">
                                            <Link
                                                href="/profile/interview-settings"
                                                onClick={() => switchProfile(profile.id)}
                                                className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-600"
                                            >
                                                Edit Settings
                                            </Link>
                                            <Link
                                                href="/profile/context-upload"
                                                onClick={() => switchProfile(profile.id)}
                                                className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-600"
                                            >
                                                Upload Context
                                            </Link>
                                            <Link
                                                href="/profile/qa-pairs"
                                                onClick={() => switchProfile(profile.id)}
                                                className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-600"
                                            >
                                                Q&A Pairs
                                            </Link>
                                            <Link
                                                href="/profile/stories"
                                                onClick={() => switchProfile(profile.id)}
                                                className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-600"
                                            >
                                                STAR Stories
                                            </Link>
                                        </div>
                                    </>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Back Link */}
                <div className="mt-8">
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                    >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
}
