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

/**
 * authDownload — download a file from an authenticated endpoint.
 *
 * A plain <a href> click can't carry the Authorization header, so fetch
 * the body with authFetch, then save it through an object URL. The
 * filename comes from the server's Content-Disposition header.
 */
export async function authDownload(url: string, fallbackFilename: string): Promise<boolean> {
    const res = await authFetch(url);
    if (!res.ok) return false;

    const disposition = res.headers.get('Content-Disposition') || '';
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : fallbackFilename;

    const objectUrl = URL.createObjectURL(await res.blob());
    const a = document.createElement('a');
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(objectUrl);
    return true;
}
