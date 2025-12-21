#!/usr/bin/env python3
"""
Compare latency: GLM vs Claude
"""
import asyncio
import time
from zhipuai import ZhipuAI
from anthropic import Anthropic

GLM_KEY = "6a6233acc6c04b5892f64a5719d88b64.oPrVA8iHBbP0KMQ3"
# CLAUDE_KEY from env

question = "Tell me about yourself in 3 bullets"

print("Latency Comparison: GLM vs Claude")
print("=" * 60)

# Test GLM
print("\n[1] Testing GLM-4-Flashx (China server)...")
glm_client = ZhipuAI(api_key=GLM_KEY)

start = time.time()
try:
    response = glm_client.chat.completions.create(
        model="glm-4-flashx",
        messages=[{"role": "user", "content": question}],
        max_tokens=100,
        stream=False
    )
    glm_time = (time.time() - start) * 1000
    print(f"✓ GLM Response time: {glm_time:.0f}ms")
    print(f"  Answer length: {len(response.choices[0].message.content)} chars")
except Exception as e:
    print(f"✗ GLM failed: {e}")
    glm_time = 999999

# Test Claude
print("\n[2] Testing Claude Sonnet 4.5 (US server)...")
import os
claude_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

start = time.time()
try:
    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": question}]
    )
    claude_time = (time.time() - start) * 1000
    print(f"✓ Claude Response time: {claude_time:.0f}ms")
    print(f"  Answer length: {len(response.content[0].text)} chars")
except Exception as e:
    print(f"✗ Claude failed: {e}")
    claude_time = 999999

# Compare
print("\n" + "=" * 60)
print("RESULTS:")
print(f"  GLM:    {glm_time:.0f}ms")
print(f"  Claude: {claude_time:.0f}ms")

if glm_time < claude_time:
    diff = claude_time - glm_time
    print(f"  Winner: GLM is {diff:.0f}ms faster ✓")
else:
    diff = glm_time - claude_time
    print(f"  Winner: Claude is {diff:.0f}ms faster ✓")
    print(f"\n⚠️ GLM slower due to China server location")
    print(f"   Recommendation: Use Claude for production (lower latency)")

print("=" * 60)
