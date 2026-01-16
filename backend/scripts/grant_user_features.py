#!/usr/bin/env python3
"""
Grant credits and features to a specific user.
Run from backend directory: python -m scripts.grant_user_features
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings


def grant_user_features(email: str, credits: int = 100):
    """Grant credits and all one-time features to a user by email."""

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    # 1. Find user by email
    print(f"Looking up user: {email}")

    user_result = supabase.auth.admin.list_users()
    user_id = None

    for user in user_result:
        if hasattr(user, 'email') and user.email == email:
            user_id = user.id
            break

    if not user_id:
        print(f"ERROR: User with email '{email}' not found!")
        return False

    print(f"Found user ID: {user_id}")

    # 2. Check if admin_grant plan exists, create if not
    plan_check = supabase.table("pricing_plans").select("*").eq("plan_code", "admin_grant").execute()

    if not plan_check.data:
        print("Creating admin_grant plan...")
        supabase.table("pricing_plans").insert({
            "plan_code": "admin_grant",
            "plan_name": "Admin Grant",
            "plan_type": "credits",
            "description": "Administrative credit grant",
            "price_usd": 0.00,
            "credits_amount": 100,
            "features": ["interview_practice"],
            "is_active": False,
            "display_order": 999
        }).execute()

    # 3. Grant credits
    print(f"Granting {credits} credits...")
    supabase.table("user_subscriptions").insert({
        "user_id": user_id,
        "plan_code": "admin_grant",
        "plan_type": "credits",
        "status": "active",
        "credits_total": credits,
        "credits_used": 0,
        "credits_remaining": credits,
        "metadata": {"granted_by": "admin", "reason": "promotional grant"}
    }).execute()
    print(f"✓ Granted {credits} credits")

    # 4. Grant AI Generator (if not owned)
    existing_ai = supabase.table("user_subscriptions")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("plan_code", "ai_generator")\
        .in_("status", ["active", "depleted"])\
        .execute()

    if not existing_ai.data:
        supabase.table("user_subscriptions").insert({
            "user_id": user_id,
            "plan_code": "ai_generator",
            "plan_type": "one_time",
            "status": "active",
            "usage_count": 0,
            "usage_limit": None,
            "metadata": {"granted_by": "admin", "reason": "promotional grant"}
        }).execute()
        print("✓ Granted AI Q&A Generator")
    else:
        print("- AI Q&A Generator already owned")

    # 5. Grant Q&A Management (if not owned)
    existing_qa = supabase.table("user_subscriptions")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("plan_code", "qa_management")\
        .in_("status", ["active", "depleted"])\
        .execute()

    if not existing_qa.data:
        supabase.table("user_subscriptions").insert({
            "user_id": user_id,
            "plan_code": "qa_management",
            "plan_type": "one_time",
            "status": "active",
            "usage_count": 0,
            "usage_limit": None,
            "metadata": {"granted_by": "admin", "reason": "promotional grant"}
        }).execute()
        print("✓ Granted Q&A Management")
    else:
        print("- Q&A Management already owned")

    print(f"\n✅ Successfully granted all features to {email}")
    return True


def grant_credits_and_ai_generator(email: str, credits: int):
    """Grant only credits and AI Generator to a user."""

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    # Find user by email
    print(f"Looking up user: {email}")

    user_result = supabase.auth.admin.list_users()
    user_id = None

    for user in user_result:
        if hasattr(user, 'email') and user.email == email:
            user_id = user.id
            break

    if not user_id:
        print(f"ERROR: User with email '{email}' not found!")
        return False

    print(f"Found user ID: {user_id}")

    # Grant credits
    print(f"Granting {credits} credits...")
    supabase.table("user_subscriptions").insert({
        "user_id": user_id,
        "plan_code": "admin_grant",
        "plan_type": "credits",
        "status": "active",
        "credits_total": credits,
        "credits_used": 0,
        "credits_remaining": credits,
        "metadata": {"granted_by": "admin", "reason": "promotional grant"}
    }).execute()
    print(f"Granted {credits} credits")

    # Grant AI Generator only
    existing_ai = supabase.table("user_subscriptions")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("plan_code", "ai_generator")\
        .in_("status", ["active", "depleted"])\
        .execute()

    if not existing_ai.data:
        supabase.table("user_subscriptions").insert({
            "user_id": user_id,
            "plan_code": "ai_generator",
            "plan_type": "one_time",
            "status": "active",
            "usage_count": 0,
            "usage_limit": None,
            "metadata": {"granted_by": "admin", "reason": "promotional grant"}
        }).execute()
        print("Granted AI Q&A Generator")
    else:
        print("AI Q&A Generator already owned")

    print(f"Done for {email}")
    return True


if __name__ == "__main__":
    # Grant 47 credits + AI Generator to these users
    users = [
        "moon.econlaw@gmail.com",
        "yoosunna0707@gmail.com"
    ]

    for email in users:
        print(f"\n--- Processing {email} ---")
        grant_credits_and_ai_generator(email, 47)
