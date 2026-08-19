import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Automatically resolve environment: production on Render or if FLASK_ENV=production or DATABASE_URL is set
is_prod = (
    os.environ.get('FLASK_ENV') == 'production' or
    os.environ.get('RENDER') is not None or
    (os.environ.get('DATABASE_URL') is not None and os.environ.get('FLASK_ENV') != 'development')
)
config_name = 'production' if is_prod else os.environ.get('FLASK_ENV', 'development')

app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

