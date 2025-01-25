#!/bin/bash
gunicorn web_app:app --worker-class eventlet --bind 0.0.0.0:$PORT 