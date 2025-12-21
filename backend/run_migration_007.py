"""
Run migration 007 to update Q&A pairs with truthful answers
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def run_migration():
    # Read migration file
    with open('database/migrations/007_truthful_answers.sql', 'r') as f:
        sql = f.read()

    # Connect to database
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    try:
        # Execute migration
        result = await conn.fetch(sql)
        print("✅ Migration completed successfully!")
        print(f"\nUpdated answers:")
        for row in result:
            print(f"  - {row['question'][:50]}...")
            print(f"    {row['answer_preview']}...\n")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
