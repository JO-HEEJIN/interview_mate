'use client';

/**
 * Profile selector dropdown for switching between interview profiles
 * Displays in the header, shows current profile, and allows switching/creating profiles
 */

import { useState, useRef, useEffect } from 'react';
import { useProfile, Profile } from '@/contexts/ProfileContext';
import Link from 'next/link';

interface ProfileSelectorProps {
    compact?: boolean; // For mobile view
}

export function ProfileSelector({ compact = false }: ProfileSelectorProps) {
    const { profiles, activeProfile, isLoading, switchProfile, createProfile } = useProfile();
    const [isOpen, setIsOpen] = useState(false);
    const [isCreating, setIsCreating] = useState(false);
    const [newProfileName, setNewProfileName] = useState('');
    const [createError, setCreateError] = useState<string | null>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
                setIsCreating(false);
            }
        }

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Handle profile creation
    const handleCreate = async () => {
        if (!newProfileName.trim()) {
            setCreateError('Profile name is required');
            return;
        }

        const result = await createProfile(newProfileName.trim());
        if (result) {
            setNewProfileName('');
            setIsCreating(false);
            setIsOpen(false);
            setCreateError(null);
        } else {
            setCreateError('Failed to create profile');
        }
    };

    // Don't show if loading or no profiles
    if (isLoading) {
        return (
            <div className="flex items-center gap-2 rounded-lg bg-zinc-100 px-3 py-2 dark:bg-zinc-800">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-400 border-t-transparent" />
                <span className="text-sm text-zinc-500">Loading...</span>
            </div>
        );
    }

    // Show create profile prompt if no profiles exist
    if (profiles.length === 0) {
        return (
            <Link
                href="/profile/interview-settings"
                className="flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-300 dark:hover:bg-blue-900"
            >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Profile
            </Link>
        );
    }

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Selector Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 ${
                    compact ? 'w-full justify-between' : ''
                }`}
            >
                <div className="flex items-center gap-2 min-w-0">
                    {/* Profile icon */}
                    <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-bold text-white">
                        {activeProfile?.profile_name?.charAt(0).toUpperCase() || 'P'}
                    </div>
                    <div className="min-w-0 flex-1">
                        <div className="truncate font-medium">
                            {activeProfile?.profile_name || 'Select Profile'}
                        </div>
                        {!compact && activeProfile?.target_role && (
                            <div className="truncate text-xs text-zinc-500 dark:text-zinc-400">
                                {activeProfile.target_role}
                                {activeProfile.target_company && ` @ ${activeProfile.target_company}`}
                            </div>
                        )}
                    </div>
                </div>
                {/* Dropdown arrow */}
                <svg
                    className={`h-4 w-4 flex-shrink-0 text-zinc-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute right-0 top-full z-50 mt-2 w-72 rounded-lg border border-zinc-200 bg-white shadow-lg dark:border-zinc-700 dark:bg-zinc-900">
                    {/* Profile List */}
                    <div className="max-h-64 overflow-y-auto p-2">
                        {profiles.map((profile) => (
                            <button
                                key={profile.id}
                                onClick={() => {
                                    switchProfile(profile.id);
                                    setIsOpen(false);
                                }}
                                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors ${
                                    activeProfile?.id === profile.id
                                        ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                                        : 'text-zinc-700 hover:bg-zinc-50 dark:text-zinc-300 dark:hover:bg-zinc-800'
                                }`}
                            >
                                {/* Profile avatar */}
                                <div className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold text-white ${
                                    activeProfile?.id === profile.id
                                        ? 'bg-gradient-to-br from-blue-500 to-purple-600'
                                        : 'bg-zinc-400 dark:bg-zinc-600'
                                }`}>
                                    {profile.profile_name.charAt(0).toUpperCase()}
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="truncate font-medium">{profile.profile_name}</span>
                                        {profile.is_default && (
                                            <span className="flex-shrink-0 rounded bg-zinc-200 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-700 dark:text-zinc-400">
                                                Default
                                            </span>
                                        )}
                                    </div>
                                    {profile.target_role && (
                                        <div className="truncate text-xs text-zinc-500 dark:text-zinc-400">
                                            {profile.target_role}
                                            {profile.target_company && ` @ ${profile.target_company}`}
                                        </div>
                                    )}
                                </div>
                                {/* Check mark for selected */}
                                {activeProfile?.id === profile.id && (
                                    <svg className="h-5 w-5 flex-shrink-0 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Divider */}
                    <div className="border-t border-zinc-200 dark:border-zinc-700" />

                    {/* Create New Profile */}
                    {isCreating ? (
                        <div className="p-3">
                            <input
                                type="text"
                                value={newProfileName}
                                onChange={(e) => {
                                    setNewProfileName(e.target.value);
                                    setCreateError(null);
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleCreate();
                                    if (e.key === 'Escape') {
                                        setIsCreating(false);
                                        setNewProfileName('');
                                    }
                                }}
                                placeholder="Profile name (e.g., Google SWE)"
                                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
                                autoFocus
                            />
                            {createError && (
                                <p className="mt-1 text-xs text-red-500">{createError}</p>
                            )}
                            <div className="mt-2 flex gap-2">
                                <button
                                    onClick={handleCreate}
                                    className="flex-1 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                                >
                                    Create
                                </button>
                                <button
                                    onClick={() => {
                                        setIsCreating(false);
                                        setNewProfileName('');
                                        setCreateError(null);
                                    }}
                                    className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm font-medium text-zinc-600 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-400 dark:hover:bg-zinc-800"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="p-2">
                            <button
                                onClick={() => setIsCreating(true)}
                                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-950"
                            >
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                Create New Profile
                            </button>
                            <Link
                                href="/profile/manage"
                                onClick={() => setIsOpen(false)}
                                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 dark:text-zinc-400 dark:hover:bg-zinc-800"
                            >
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                Manage Profiles
                            </Link>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
