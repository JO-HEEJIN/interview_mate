#!/usr/bin/env python3
"""
Fix question_type values in migration files
"""
import re

# Question type mapping by category
CATEGORY_TYPES = {
    "CATEGORY 1: RESUME / HONESTY": "behavioral",
    "CATEGORY 2: TECHNICAL - ARCHITECTURE": "technical",
    "CATEGORY 3: TECHNICAL - COST OPTIMIZATION": "technical",
    "CATEGORY 4: TECHNICAL - SAFETY": "technical",
    "CATEGORY 5: BEHAVIORAL": "behavioral",
    "CATEGORY 6: SOLUTIONS ARCHITECT ROLE": "general",
    "CATEGORY 7: KOREA": "general",
    "CATEGORY 8: BIRTH2DEATH": "general",
    "CATEGORY 9: FUTURE PLANS": "general",
    "CATEGORY 10: EDGE CASES": "situational",
}

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    current_type = None
    lines = content.split('\n')
    result_lines = []

    for line in lines:
        # Check if we're entering a new category
        for category, qtype in CATEGORY_TYPES.items():
            if category in line:
                current_type = qtype
                break

        # Fix INSERT statements
        if 'INSERT INTO public.qa_pairs' in line and current_type:
            # Add question_type value before the closing parenthesis
            if line.endswith('VALUES'):
                result_lines.append(line)
            elif 'question_type) VALUES' in line:
                # Already has question_type column
                result_lines.append(line)
            else:
                result_lines.append(line)
        elif line.strip().endswith("');") and current_type and len(result_lines) > 0:
            # This is the end of an INSERT statement
            # Replace the last line
            prev_line = result_lines[-1]
            if not prev_line.strip().endswith(f"'{current_type}');"):
                # Fix the closing
                result_lines[-1] = prev_line.rstrip()[:-2] + f",\n    '{current_type}');"
                continue
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)

    with open(filepath, 'w') as f:
        f.write('\n'.join(result_lines))

if __name__ == '__main__':
    files = [
        'database/migrations/017_openai_interview_qa_pairs.sql',
        'database/migrations/018_openai_interview_qa_pairs_part2.sql',
        'database/migrations/019_openai_interview_qa_pairs_part3.sql',
    ]

    for filepath in files:
        print(f"Fixing {filepath}...")
        fix_file(filepath)

    print("Done!")
