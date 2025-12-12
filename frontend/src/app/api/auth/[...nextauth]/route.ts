import NextAuth from 'next-auth';
import type { AuthOptions, Session, User, Account } from 'next-auth';
import type { JWT } from 'next-auth/jwt';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import { supabase } from '@/lib/supabase';
import bcrypt from 'bcryptjs';

export const authOptions: AuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || '',
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
        }),
        GitHubProvider({
            clientId: process.env.GITHUB_CLIENT_ID || '',
            clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
        }),
        CredentialsProvider({
            name: 'credentials',
            credentials: {
                email: { label: 'Email', type: 'email' },
                password: { label: 'Password', type: 'password' },
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) {
                    return null;
                }

                const { data: user, error } = await supabase
                    .from('profiles')
                    .select('*')
                    .eq('email', credentials.email)
                    .single();

                if (error || !user) {
                    return null;
                }

                // For OAuth users, they should use OAuth login
                if (!user.password_hash) {
                    return null;
                }

                const isValid = await bcrypt.compare(
                    credentials.password as string,
                    user.password_hash
                );

                if (!isValid) {
                    return null;
                }

                return {
                    id: user.id,
                    email: user.email,
                    name: user.full_name,
                    image: user.avatar_url,
                };
            },
        }),
    ],
    pages: {
        signIn: '/auth/login',
        error: '/auth/error',
    },
    callbacks: {
        async jwt({ token, user, account }: { token: JWT; user?: User; account?: Account | null }) {
            if (user) {
                token.id = user.id;
            }
            if (account) {
                token.accessToken = account.access_token;
                token.provider = account.provider;
            }
            return token;
        },
        async session({ session, token }: { session: Session; token: JWT }) {
            if (session.user) {
                session.user.id = token.id as string;
            }
            return session;
        },
        async signIn({ user, account }: { user: User; account: Account | null }) {
            if (account?.provider === 'google' || account?.provider === 'github') {
                // Upsert user profile for OAuth users
                const { error } = await supabase.from('profiles').upsert(
                    {
                        id: user.id,
                        email: user.email,
                        full_name: user.name,
                        avatar_url: user.image,
                    },
                    { onConflict: 'id' }
                );

                if (error) {
                    console.error('Error upserting user:', error);
                    return false;
                }
            }
            return true;
        },
    },
    session: {
        strategy: 'jwt',
    },
    secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
