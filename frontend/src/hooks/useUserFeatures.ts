/**
 * useUserFeatures hook
 * Fetches and manages user subscription features and credits
 */

import { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UserFeatures {
  interview_credits: number;
  ai_generator_available: boolean;
  qa_management_available: boolean;
  isLoading: boolean;
  error: string | null;
}

export function useUserFeatures(userId: string | null) {
  const [features, setFeatures] = useState<UserFeatures>({
    interview_credits: 0,
    ai_generator_available: false,
    qa_management_available: false,
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

      const response = await fetch(`${API_URL}/api/subscriptions/${userId}/summary`);

      if (!response.ok) {
        throw new Error('Failed to fetch user features');
      }

      const data = await response.json();

      setFeatures({
        interview_credits: data.interview_credits || 0,
        ai_generator_available: data.ai_generator_available || false,
        qa_management_available: data.qa_management_available || false,
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
