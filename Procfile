web: .venv/bin/python -m gunicorn application:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --preload --log-level info
