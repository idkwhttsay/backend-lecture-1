#!/bin/sh
if [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_KEY_PATH" ]; then
  exec uvicorn src.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile "$SSL_KEY_PATH" --ssl-certfile "$SSL_CERT_PATH"
else
  exec uvicorn src.main:app --host 0.0.0.0 --port 8000
fi