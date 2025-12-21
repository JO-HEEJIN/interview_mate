#!/usr/bin/env python3
"""
Test GLM API connection and model availability
"""
from zhipuai import ZhipuAI
import os

API_KEY = "6a6233acc6c04b5892f64a5719d88b64.oPrVA8iHBbP0KMQ3"

print("Testing GLM API Connection...")
print("=" * 50)

try:
    client = ZhipuAI(api_key=API_KEY)

    # Test 1: Simple completion
    print("\n[Test 1] Simple completion with glm-4-flashx...")
    try:
        response = client.chat.completions.create(
            model="glm-4-flashx",
            messages=[
                {"role": "user", "content": "Say 'Hello' in one word"}
            ],
            max_tokens=10
        )
        print(f"✓ Success: {response.choices[0].message.content}")
    except Exception as e:
        print(f"✗ Failed with glm-4-flashx: {str(e)}")

        # Try alternative model names
        print("\n[Test 2] Trying glm-4-flash...")
        try:
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": "Say 'Hello' in one word"}
                ],
                max_tokens=10
            )
            print(f"✓ Success: {response.choices[0].message.content}")
            print("\n⚠️ USE 'glm-4-flash' NOT 'glm-4-flashx'")
        except Exception as e2:
            print(f"✗ Also failed with glm-4-flash: {str(e2)}")

            # Try glm-4-air
            print("\n[Test 3] Trying glm-4-air...")
            try:
                response = client.chat.completions.create(
                    model="glm-4-air",
                    messages=[
                        {"role": "user", "content": "Say 'Hello' in one word"}
                    ],
                    max_tokens=10
                )
                print(f"✓ Success: {response.choices[0].message.content}")
                print("\n⚠️ USE 'glm-4-air' NOT 'glm-4-flashx'")
            except Exception as e3:
                print(f"✗ Also failed with glm-4-air: {str(e3)}")
                print("\n❌ ALL MODELS FAILED - API KEY ISSUE?")

except Exception as e:
    print(f"\n❌ Client initialization failed: {str(e)}")
    print("Check API key and network connection")

print("\n" + "=" * 50)
