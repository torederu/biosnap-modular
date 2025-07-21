# Biometric Snapshot Streamlit App

## Project Structure

- `main.py` — Main entry point, handles layout and tab switching
- `components/` — Each tab as a separate module
- `utils/` — Utility functions (scraping, redaction, etc.)
- `supabase_utils.py` — Supabase setup and helpers
- `auth.py` — Authentication logic
- `config.yaml` — Authenticator config (not tracked in git)
- `.env` — Supabase credentials (not tracked in git)
- `requirements.txt` — Python dependencies

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your `.env` and `config.yaml` files to the project root.
3. Run the app:
   ```bash
   streamlit run main.py
   ```

## Adding Tabs

- Add new tab modules to `components/` and import them in `main.py`.

## Security

- Never commit `.env` or `config.yaml` to git. 