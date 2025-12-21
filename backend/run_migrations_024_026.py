"""
Run migrations 024, 025, 026 for context upload feature
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def run_migrations():
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")
        return

    supabase = create_client(supabase_url, supabase_key)

    migrations = [
        'database/migrations/024_user_contexts.sql',
        'database/migrations/025_qa_pairs_extensions.sql',
        'database/migrations/026_generation_batches.sql',
    ]

    for migration_file in migrations:
        print(f"\n{'='*60}")
        print(f"Running: {migration_file}")
        print('='*60)

        try:
            with open(migration_file, 'r') as f:
                sql = f.read()

            # Execute migration using Supabase RPC
            # Note: This requires direct SQL execution which Supabase Python SDK doesn't support well
            # Better to use psql or Supabase dashboard

            print(f"⚠️  Please run this migration manually via Supabase dashboard or psql:")
            print(f"\nSQL content preview:")
            print(sql[:500] + "...")
            print(f"\nOr run: psql $DATABASE_URL < {migration_file}")

        except Exception as e:
            print(f"❌ Error reading {migration_file}: {e}")

if __name__ == "__main__":
    print("\n🚀 Context Upload Migrations (024-026)\n")
    run_migrations()
    print("\n" + "="*60)
    print("📝 To run migrations, use one of these methods:")
    print("   1. Supabase Dashboard → SQL Editor → paste migration content")
    print("   2. psql $DATABASE_URL < database/migrations/024_user_contexts.sql")
    print("   3. Use Supabase CLI: supabase db push")
    print("="*60 + "\n")
