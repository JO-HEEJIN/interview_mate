/**
 * useUserFeatures hook
 * Fetches and manages user subscription features and credits
 */

import { useState, useEffect, useCallback } from 'react';
import { authFetch } from '@/lib/authFetch';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type FeatureSource = 'purchased' | 'first_profile_free' | 'locked';

export interface UserFeatures {
  interview_credits: number;
  ai_generator_available: boolean;
  qa_management_available: boolean;
  ai_generator_source: FeatureSource;
  qa_management_source: FeatureSource;
  profile_count: number;
  isLoading: boolean;
  error: string | null;
}

export function useUserFeatures(userId: string | null) {
  const [features, setFeatures] = useState<UserFeatures>({
    interview_credits: 0,
    ai_generator_available: false,
    qa_management_available: false,
    ai_generator_source: 'locked',
    qa_management_source: 'locked',
    profile_count: 0,
    isLoading: true,
    error: null,
  });

  const fetchFeatures = useCallback(async () => {
    if (!userId) {
      setFeatures(prev => ({ ...prev, isLoading: false }));
      return;
    }

    try {
      setFeatures(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await authFetch(`${API_URL}/api/subscriptions/${userId}/summary`);

      if (!response.ok) {
        throw new Error('Failed to fetch user features');
      }

      const data = await response.json();

      setFeatures({
        interview_credits: data.interview_credits || 0,
        ai_generator_available: data.ai_generator_available || false,
        qa_management_available: data.qa_management_available || false,
        ai_generator_source: data.ai_generator_source || 'locked',
        qa_management_source: data.qa_management_source || 'locked',
        profile_count: data.profile_count ?? 0,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      console.error('Error fetching user features:', err);
      setFeatures(prev => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
    }
  }, [userId]);

  useEffect(() => {
    fetchFeatures();
  }, [fetchFeatures]);

  // Expose refetch function for manual refresh (e.g., after purchase)
  const refetch = useCallback(() => {
    fetchFeatures();
  }, [fetchFeatures]);

  return { ...features, refetch };
}
