#!/bin/sh
set -eu

escape_js_string() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

api_base_url="$(escape_js_string "${VITE_API_BASE_URL:-/api}")"
umami_script_url="$(escape_js_string "${UMAMI_SCRIPT_URL:-}")"
umami_website_id="$(escape_js_string "${UMAMI_WEBSITE_ID:-}")"
umami_host_url="$(escape_js_string "${UMAMI_HOST_URL:-}")"

cat <<EOF >/usr/share/nginx/html/env.js
window.__APP_ENV__ = {
  API_BASE_URL: "${api_base_url}",
  UMAMI_SCRIPT_URL: "${umami_script_url}",
  UMAMI_WEBSITE_ID: "${umami_website_id}",
  UMAMI_HOST_URL: "${umami_host_url}"
};
EOF

exec "$@"
