#!/usr/bin/env python3
import subprocess
import os
import json
from pathlib import Path

# ===== CONFIGURATION =====
GEMINI_CLI_PATH = r"d:\Users\NamoNexus Enterprise v3.5.1\gemini-cli-source\packages\cli"
PROJECT_ROOT = Path(__file__).parent.parent
MAX_REFINEMENT_LOOPS = 2

# Prompts for different roles
PROMPT_REASONING = """
You are the **Reasoning Agent**. Your job is to analyze the following problem and provide a step-by-step STRATEGY for solving it.
Do NOT write the code yourself. Focus on the logic, algorithm, and potential pitfalls.
Problem: {input}
"""

PROMPT_CODER = """
You are the **Coder Agent** (Codex simulation). Your job is to write valid Python code based on the following STRATEGY.
Output ONLY the code block.
Strategy: {strategy}
"""

PROMPT_REVIEW = """
You are the **Reasoning Agent** reviewing code.
Strategy: {strategy}
Code:
{code}

Does this code follow the strategy and logic correctly? 
If YES, reply exactly: "APPROVED".
If NO, provide specific feedback on what needs to be fixed.
"""


def run_gemini_source(prompt):
    """Runs Gemini CLI from source with the given prompt."""
    try:
        # Use npm run start -- prompt "..." to call the CLI from source
        # We need to be in the CLI directory for this to work relative dependencies
        cmd = ["npm", "run", "start", "--", "prompt", prompt]

        print(f"🤖 Calling Gemini (Source)...")
        result = subprocess.run(
            cmd,
            cwd=GEMINI_CLI_PATH,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,  # Needed for npm on Windows sometimes, or use npm.cmd
        )

        if result.returncode != 0:
            print(f"❌ Error running Gemini CLI: {result.stderr}")
            return None

        # Extract the response (simple parsing, might need adjustment based on CLI output format)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def reasoning_step(user_input):
    print("\n🔹 [Step 1] Reasoning Agent: Analyzing problem...")
    prompt = PROMPT_REASONING.format(input=user_input)
    response = run_gemini_source(prompt)
    print(f"📋 Strategy Proposed:\n{response}\n")
    return response


def coding_step(strategy):
    print("\n🔹 [Step 2] Coder Agent: Generating code...")
    prompt = PROMPT_CODER.format(strategy=strategy)
    response = run_gemini_source(prompt)

    # Simple extraction of code block if present
    code = response
    if "```python" in response:
        code = response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        code = response.split("```")[1].split("```")[0].strip()

    print(f"💻 Code Generated:\n{code}\n")
    return code


def refinement_loop(strategy, initial_code):
    current_code = initial_code

    for i in range(MAX_REFINEMENT_LOOPS):
        print(f"\n🔄 [Step 3.{i + 1}] Refinement Loop...")

        # Review
        review_prompt = PROMPT_REVIEW.format(strategy=strategy, code=current_code)
        review_result = run_gemini_source(review_prompt)
        print(f"🧐 Review Result: {review_result}")

        if "APPROVED" in review_result:
            print("✅ Code Approved by Reasoning Agent.")
            return current_code

        # Refine (Simulated Coder fixing based on feedback)
        print("🔧 Coder Agent: Fixing code based on feedback...")
        fix_prompt = f"""
        You are the Coder Agent. Fix the following code based on the feedback.
        Original Strategy: {strategy}
        Current Code:
        {current_code}
        Feedback: {review_result}
        
        Output ONLY the fixed code key.
        """
        current_code = run_gemini_source(fix_prompt)

        # Strip markdown again if needed
        if "```" in current_code:
            try:
                if "```python" in current_code:
                    current_code = (
                        current_code.split("```python")[1].split("```")[0].strip()
                    )
                else:
                    current_code = current_code.split("```")[1].split("```")[0].strip()
            except:
                pass  # use raw if split fails

        print(f"🛠️  Fixed Code:\n{current_code}\n")

    print("⚠️ Max loops reached. Using last version.")
    return current_code


def save_code(code, filename="generated_fix.py"):
    filepath = PROJECT_ROOT / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"\n💾 Saved code to: {filepath}")
    return filepath


def main():
    print("🚀 Starting Multi-Agent Orchestrator (Gemini Source Powered)")

    # 1. Get Task
    try:
        user_task = input("Enter the task/bug description: ")
        if not user_task:
            print("❌ No task provided.")
            return

        # 2. Reasoning
        strategy = reasoning_step(user_task)
        if not strategy:
            return

        # 3. Coding
        initial_code = coding_step(strategy)
        if not initial_code:
            return

        # 4. Refinement
        final_code = refinement_loop(strategy, initial_code)

        # 5. Output
        save_code(final_code)
        print("\n✨ Workflow Complete!")

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled.")


if __name__ == "__main__":
    main()
