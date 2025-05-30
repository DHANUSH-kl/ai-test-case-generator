from waitress import serve
from backend.app import app  # since backend is a subfolder

if __name__ == '__main__':
    print("Starting Waitress server on http://0.0.0.0:8000")
    serve(app, host='0.0.0.0', port=8000)
