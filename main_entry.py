import os, sys; wf = os.environ.get("REPL_WORKFLOW", ""); print(f"WORKFLOW: {wf}"); (wf == "run_miku_bot") and __import__("os").system("python direct_bot_runner.py") and sys.exit(0)
