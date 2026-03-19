import sys
import subprocess
import tempfile
import os
from agents import PythonCodingStandards

def run_command(cmd):
    """Executes a bash command and returns the string output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"Stderr: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pr_reviewer.py <PR_NUMBER>")
        sys.exit(1)
        
    pr_number = sys.argv[1]
    
    print(f"[*] Fetching git diff for PR #{pr_number} via GitHub CLI...")
    diff_text = run_command(f"gh pr diff {pr_number}")
    
    if not diff_text:
        print("[!] The diff is empty or PR could not be found.")
        sys.exit(0)
        
    print("[*] PR Diff successfully extracted from GitHub.")
    print("[*] Delegating the diff to the Python Coding Standards Agent...\n")
    
    # Instantiate the standard checking agent
    agent = PythonCodingStandards()
    
    # Bundle the task user prompt
    task_prompt = (
        "Please review the following git diff for a GitHub Pull Request. "
        "Provide a concise, highly actionable code review targeting any potential bugs, security issues, "
        "or PEP8 styling failures. Use markdown to format the review beautifully for a GitHub comment.\n\n"
        f"Diff:\n```diff\n{diff_text}\n```"
    )
    
    # Execute through the LLM brain (or the simulated mock loop)
    review_response = agent.execute_task(task_prompt)
    
    print("=== Agent Analysis Output ===")
    print(review_response)
    print("=============================\n")
    
    # Skip posting if it's just a MOCK output for local tests without an API key
    if "[MOCK]" in review_response or "[SIMULATED]" in review_response:
        print("[!] Agent is running in MOCK mode. Will not post this to real GitHub.")
        sys.exit(0)
    
    print(f"[*] Publishing AI review as a comment to PR #{pr_number}...")
    
    # We write the LLM's raw markdown output to a temporary file 
    # to avoid messy string-character escaping in bash.
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(review_response)
        temp_file = f.name
        
    try:
        run_command(f"gh pr review {pr_number} --comment -F {temp_file}")
        print(f"[+] Successfully posted the intelligent Agent review to PR #{pr_number} on GitHub! 🎉")
    finally:
        os.remove(temp_file)

if __name__ == "__main__":
    main()
