# Palimpsest-Observer

A neutral “governance probe” that signs every AI context window and flags contradictions before the LLM call.

---

## Quick Start

```bash
# 1. clone & enter
git clone https://github.com/<your-user>/palobserver.git
cd palobserver

# 2. create env & install in editable mode
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 3. generate a signing key (first run only)
python - <<'PY'
from palobserver.crypto import generate_key
generate_key()
print("Keypair written to observer.pem")
PY

# 4. run the sample demo (needs OPENAI_API_KEY env var)
export OPENAI_API_KEY="sk-..."   # set your key once
python demo_retrieval.py
# → prints: Palimpsest bundle <id>  conflicts: 1

# 5. view recent bundles
pal ledger ls --limit 5

