#!/bin/bash
curl -k -s https://memo.myisland.dev/health 2>/dev/null | jq -r '.data.environment | if .mode == "development" then "🛠️ DEBUG MODE" else "🚀 PRODUCTION MODE" end' 2>/dev/null
