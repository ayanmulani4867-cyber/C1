import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Automatically resolve environment: production on Vercel/Render or if FLASK_ENV=production
is_prod = (
    os.environ.get('FLASK_ENV') == 'production' or
    os.environ.get('VERCEL') is not None or
    os.environ.get('RENDER') is not None
)
config_name = 'production' if is_prod else os.environ.get('FLASK_ENV', 'development')

app = create_app(config_name)
application = app

if __name__ == '__main__':
    from app.extensions import socketio
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

