/**
 * authFetch — fetch wrapper that attaches the Supabase JWT as a
 * Bearer token in the Authorization header.
 *
 * Use for any backend endpoint that calls require_user_match() on
 * the server (currently subscriptions + context_upload surfaces;
 * other files follow in subsequent PRs).
 *
 * Identical signature to global fetch so call sites only need to
 * swap `fetch(` → `authFetch(`.
 *
 * Falls back to a normal fetch (no header) if the session can't be
 * read — the backend will then return 401, which is the right
 * outcome for a not-authenticated user.
 */

import { supabase } from '@/lib/supabase';

export async function authFetch(
    input: RequestInfo | URL,
    init?: RequestInit,
): Promise<Response> {
    const headers = new Headers(init?.headers);
    try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
            headers.set('Authorization', `Bearer ${session.access_token}`);
        }
    } catch {
        // If session lookup blows up, send the request without auth —
        // backend will 401 and the UI surfaces it as a normal error.
    }
    return fetch(input, { ...init, headers });
}
