#!/bin/bash
curl -k -s https://${DOMAIN:-localhost}/health 2>/dev/null | jq -r '.data.environment | if .mode == "development" then "🛠️ DEBUG MODE" else "🚀 PRODUCTION MODE" end' 2>/dev/null
