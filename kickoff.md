Act as an Expert Release Engineer and Senior Software Architect. 
I am assigning you the implementation of the "Release Engineering and Offline Operations" workstream for our AI Agent project.

I am providing you with two specification documents:
1. SOFTWARE_PROJECT_GUIDELINES.md - The strict global project standards.
2. RELEASE_ENGINEERING_WORKSTREAM.md - The specific requirements for this module.

CRITICAL CONSTRAINTS YOU MUST FOLLOW:
1. File Size Limit: NO code file may exceed 150 lines of code (excluding blanks/comments). You MUST split logic into smaller modules (e.g., helpers, constants) if a file gets too long.
2. Strict Boundaries: You are ONLY allowed to create/modify files in the directories explicitly allowed in the Workstream Spec (e.g., .github/workflows/, tools/offline_ops/, tests/offline_ops/). You MUST NOT modify, mock, or touch any game logic.
3. Tech Stack: Use only `pathlib` and `subprocess` for the CLI. No shell strings. No network calls. 
4. CLI Contract: The CLI must return the exact exit codes (0-7) defined in the spec.
5. Code Quality: Fully typed Python, comprehensive docstrings, zero hardcoded secrets, and 100% compliant with Ruff linters.

HOW WE WILL WORK:
Do NOT write all the code at once. We will do this iteratively to ensure perfect Git history and code quality.

Step 1: Read both documents carefully.
Step 2: Generate the content for `docs/TODO.md` (as required by the Guidelines). Break the implementation down into 3-4 logical phases. For each task, include Priority, Status, Owner (Nadav), and a strict Definition of Done.
Step 3: Stop and wait for my approval. Do NOT write any Python or YAML code yet.

Please acknowledge these instructions and provide the content for `docs/TODO.md` to begin.