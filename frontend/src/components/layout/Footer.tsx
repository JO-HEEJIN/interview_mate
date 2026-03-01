'use client';

import { usePathname } from 'next/navigation';

export function Footer() {
    const pathname = usePathname();

    // Don't show footer on auth pages
    if (pathname?.startsWith('/auth')) {
        return null;
    }

    return (
        <footer className="border-t border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <div className="flex flex-col items-center gap-2 text-center text-sm text-zinc-600 dark:text-zinc-400">
                    <p>
                        Questions or issues? Contact us at{' '}
                        <a
                            href="mailto:info@birth2death.com"
                            className="text-zinc-900 underline hover:text-zinc-700 dark:text-zinc-200 dark:hover:text-zinc-300"
                        >
                            info@birth2death.com
                        </a>
                    </p>
                    <p>&copy; 2026 Birth2Death LLC</p>
                </div>
            </div>
        </footer>
    );
}
