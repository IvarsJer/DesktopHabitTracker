"""Start the Flask app in-process and present as a native desktop window."""
import threading
import os
import webview
from app import create_app

flask_app = create_app()


# run Flask in a background thread
def run_flask():
    port = int(os.getenv("PORT", 5001))
    flask_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


threading.Thread(target=run_flask, daemon=True).start()

# open a native window pointing to the local server
port = int(os.getenv("PORT", 5001))
window = webview.create_window("HabitFlow", f"http://127.0.0.1:{port}/")
webview.start()
