'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { supabase } from '@/lib/supabase';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface Profile {
    id: string;
    user_id: string;
    profile_name: string;
    full_name?: string;
    target_role?: string;
    target_company?: string;
    projects_summary?: string;
    technical_stack?: string[];
    answer_style: 'concise' | 'balanced' | 'detailed';
    key_strengths?: string[];
    custom_instructions?: string;
    is_default: boolean;
    created_at: string;
    updated_at: string;
}

interface ProfileContextType {
    profiles: Profile[];
    activeProfile: Profile | null;
    isLoading: boolean;
    error: string | null;
    switchProfile: (profileId: string) => void;
    createProfile: (name: string, data?: Partial<Profile>) => Promise<Profile | null>;
    updateProfile: (profileId: string, data: Partial<Profile>) => Promise<Profile | null>;
    deleteProfile: (profileId: string) => Promise<boolean>;
    duplicateProfile: (profileId: string, newName: string) => Promise<Profile | null>;
    setDefaultProfile: (profileId: string) => Promise<boolean>;
    refreshProfiles: () => Promise<void>;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

interface ProfileProviderProps {
    children: ReactNode;
}

export function ProfileProvider({ children }: ProfileProviderProps) {
    const [profiles, setProfiles] = useState<Profile[]>([]);
    const [activeProfile, setActiveProfile] = useState<Profile | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userId, setUserId] = useState<string | null>(null);

    // Load profiles when user is authenticated
    const loadProfiles = useCallback(async (uid: string) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await fetch(`${API_URL}/api/interview-profiles/${uid}`);

            if (!response.ok) {
                throw new Error('Failed to load profiles');
            }

            const data = await response.json();
            const loadedProfiles = data.profiles || [];
            setProfiles(loadedProfiles);

            // Set active profile (default or first)
            if (loadedProfiles.length > 0) {
                const defaultProfile = loadedProfiles.find((p: Profile) => p.is_default);
                const storedProfileId = localStorage.getItem('activeProfileId');

                // Try to restore last used profile
                if (storedProfileId) {
                    const storedProfile = loadedProfiles.find((p: Profile) => p.id === storedProfileId);
                    if (storedProfile) {
                        setActiveProfile(storedProfile);
                        return;
                    }
                }

                // Fall back to default or first profile
                setActiveProfile(defaultProfile || loadedProfiles[0]);
            } else {
                setActiveProfile(null);
            }
        } catch (err) {
            console.error('Failed to load profiles:', err);
            setError('Failed to load profiles');
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Check auth and load profiles
    useEffect(() => {
        const checkAuth = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (session?.user?.id) {
                setUserId(session.user.id);
                await loadProfiles(session.user.id);
            } else {
                setIsLoading(false);
            }
        };

        checkAuth();

        const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
            if (session?.user?.id) {
                setUserId(session.user.id);
                await loadProfiles(session.user.id);
            } else {
                setUserId(null);
                setProfiles([]);
                setActiveProfile(null);
                setIsLoading(false);
            }
        });

        return () => subscription.unsubscribe();
    }, [loadProfiles]);

    // Switch to a different profile
    const switchProfile = useCallback((profileId: string) => {
        const profile = profiles.find(p => p.id === profileId);
        if (profile) {
            setActiveProfile(profile);
            localStorage.setItem('activeProfileId', profileId);
        }
    }, [profiles]);

    // Create a new profile
    const createProfile = useCallback(async (name: string, data?: Partial<Profile>): Promise<Profile | null> => {
        if (!userId) return null;

        try {
            const response = await fetch(`${API_URL}/api/interview-profiles/${userId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    profile_name: name,
                    ...data,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create profile');
            }

            const { profile } = await response.json();

            // Refresh profiles list
            await loadProfiles(userId);

            // Switch to new profile
            setActiveProfile(profile);
            localStorage.setItem('activeProfileId', profile.id);

            return profile;
        } catch (err: any) {
            console.error('Failed to create profile:', err);
            setError(err.message);
            return null;
        }
    }, [userId, loadProfiles]);

    // Update an existing profile
    const updateProfile = useCallback(async (profileId: string, data: Partial<Profile>): Promise<Profile | null> => {
        if (!userId) return null;

        try {
            const response = await fetch(`${API_URL}/api/interview-profiles/${userId}/${profileId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update profile');
            }

            const { profile } = await response.json();

            // Update local state
            setProfiles(prev => prev.map(p => p.id === profileId ? profile : p));

            if (activeProfile?.id === profileId) {
                setActiveProfile(profile);
            }

            return profile;
        } catch (err: any) {
            console.error('Failed to update profile:', err);
            setError(err.message);
            return null;
        }
    }, [userId, activeProfile]);

    // Delete a profile
    const deleteProfile = useCallback(async (profileId: string): Promise<boolean> => {
        if (!userId) return false;

        try {
            const response = await fetch(`${API_URL}/api/interview-profiles/${userId}/${profileId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to delete profile');
            }

            // Refresh profiles
            await loadProfiles(userId);

            // If deleted active profile, switch to another
            if (activeProfile?.id === profileId) {
                const remaining = profiles.filter(p => p.id !== profileId);
                if (remaining.length > 0) {
                    const newActive = remaining.find(p => p.is_default) || remaining[0];
                    setActiveProfile(newActive);
                    localStorage.setItem('activeProfileId', newActive.id);
                } else {
                    setActiveProfile(null);
                    localStorage.removeItem('activeProfileId');
                }
            }

            return true;
        } catch (err: any) {
            console.error('Failed to delete profile:', err);
            setError(err.message);
            return false;
        }
    }, [userId, activeProfile, profiles, loadProfiles]);

    // Duplicate a profile
    const duplicateProfile = useCallback(async (profileId: string, newName: string): Promise<Profile | null> => {
        if (!userId) return null;

        try {
            const response = await fetch(
                `${API_URL}/api/interview-profiles/${userId}/${profileId}/duplicate?new_name=${encodeURIComponent(newName)}`,
                { method: 'POST' }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to duplicate profile');
            }

            const { profile } = await response.json();

            // Refresh profiles
            await loadProfiles(userId);

            return profile;
        } catch (err: any) {
            console.error('Failed to duplicate profile:', err);
            setError(err.message);
            return null;
        }
    }, [userId, loadProfiles]);

    // Set default profile
    const setDefaultProfile = useCallback(async (profileId: string): Promise<boolean> => {
        if (!userId) return false;

        try {
            const response = await fetch(
                `${API_URL}/api/interview-profiles/${userId}/${profileId}/set-default`,
                { method: 'POST' }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to set default profile');
            }

            // Refresh profiles to update is_default flags
            await loadProfiles(userId);

            return true;
        } catch (err: any) {
            console.error('Failed to set default profile:', err);
            setError(err.message);
            return false;
        }
    }, [userId, loadProfiles]);

    // Refresh profiles
    const refreshProfiles = useCallback(async () => {
        if (userId) {
            await loadProfiles(userId);
        }
    }, [userId, loadProfiles]);

    const value: ProfileContextType = {
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
        refreshProfiles,
    };

    return (
        <ProfileContext.Provider value={value}>
            {children}
        </ProfileContext.Provider>
    );
}

// Custom hook to use the profile context
export function useProfile() {
    const context = useContext(ProfileContext);
    if (context === undefined) {
        throw new Error('useProfile must be used within a ProfileProvider');
    }
    return context;
}
