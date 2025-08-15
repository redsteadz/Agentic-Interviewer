#!/usr/bin/env bash
# Start script for Render

cd backend
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
