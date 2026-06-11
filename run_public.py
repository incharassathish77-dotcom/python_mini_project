"""
run_public.py — Launch Government Scheme App with a public ngrok tunnel.

Steps:
  1. Starts the Flask app on port 5000
  2. Opens an ngrok tunnel to that port
  3. Prints the public URL anyone can visit from any network/device
"""

import threading
import time
import sys
import os

# ── Make sure stdout is UTF-8 safe on Windows ────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Try importing required packages ──────────────────────────────────────────
try:
    from pyngrok import ngrok, conf
except ImportError:
    print("[ERROR] pyngrok not installed. Run:  pip install pyngrok")
    sys.exit(1)

try:
    from app import app, init_db
except ImportError as e:
    print(f"[ERROR] Could not import app.py: {e}")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────
PORT = 5000

# Optional: paste your ngrok authtoken here if you have one (free at ngrok.com)
# This removes the 2-hour session limit.
NGROK_AUTHTOKEN = ""   # e.g. "2abc123xyz_yourtoken"


def start_flask():
    """Run Flask in a background thread."""
    print(f"\n[Flask] Starting on http://127.0.0.1:{PORT} ...")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def main():
    # ── 1. Initialize database ────────────────────────────────────────────────
    init_db()

    # ── 2. Configure ngrok authtoken if provided ──────────────────────────────
    if NGROK_AUTHTOKEN.strip():
        conf.get_default().auth_token = NGROK_AUTHTOKEN
        print("[ngrok] Authtoken configured.")

    # ── 3. Start Flask in a background thread ─────────────────────────────────
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)   # Give Flask a moment to start

    # ── 4. Open ngrok tunnel ──────────────────────────────────────────────────
    try:
        tunnel = ngrok.connect(PORT, "http")
        public_url = tunnel.public_url

        print("\n" + "=" * 62)
        print("  GOVERNMENT SCHEME AWARENESS APP — PUBLIC ACCESS")
        print("=" * 62)
        print(f"\n  Local  URL : http://127.0.0.1:{PORT}")
        print(f"  Public URL : {public_url}")
        print(f"\n  Share this link with anyone on any network/device:")
        print(f"\n      --> {public_url} <--")
        print("\n  Press Ctrl+C to stop the server.")
        print("=" * 62 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Could not start ngrok tunnel: {e}")
        print("The app is still accessible locally at:")
        print(f"  http://127.0.0.1:{PORT}")
        print("\nIf you see 'ERR_NGROK_108', you need a free authtoken:")
        print("  1. Sign up free at https://dashboard.ngrok.com")
        print("  2. Copy your authtoken")
        print("  3. Paste it into NGROK_AUTHTOKEN variable in this file")
        print()

    # ── 5. Keep running until Ctrl+C ─────────────────────────────────────────
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        ngrok.kill()
        print("[INFO] Server stopped. Goodbye!")


if __name__ == "__main__":
    main()
