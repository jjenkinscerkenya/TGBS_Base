# Install uv first (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then install project in dev mode (from repo root)
uv sync --all-groups

Or with pip if they prefer:
# New way (recommended)
uv pip install -e .

To activate the virtual environment:
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows