#!/bin/bash
# init-config.sh - Initialize nanobot configuration with environment variables

set -e

CONFIG_FILE="/root/.nanobot/config.json"

echo "=========================================="
echo "Nanobot Configuration Initialization"
echo "=========================================="

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found at $CONFIG_FILE"
    exit 1
fi

echo "Found config file: $CONFIG_FILE"

# Create backup
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"
echo "Created backup: ${CONFIG_FILE}.backup"

# Replace environment variable placeholders
echo "Substituting environment variables..."

# Replace OPENROUTER_API_KEY
if [ ! -z "$OPENROUTER_API_KEY" ]; then
    sed -i "s|\${OPENROUTER_API_KEY}|$OPENROUTER_API_KEY|g" "$CONFIG_FILE"
    echo "✓ Substituted OPENROUTER_API_KEY"
else
    echo "⚠ WARNING: OPENROUTER_API_KEY not set"
fi

# Replace CEREBRAS_API_KEY (optional)
if [ ! -z "$CEREBRAS_API_KEY" ]; then
    sed -i "s|\${CEREBRAS_API_KEY}|$CEREBRAS_API_KEY|g" "$CONFIG_FILE"
    echo "✓ Substituted CEREBRAS_API_KEY"
else
    echo "ℹ CEREBRAS_API_KEY not set (optional)"
fi

# Replace TELEGRAM_BOT_TOKEN (optional)
if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
    sed -i "s|\${TELEGRAM_BOT_TOKEN}|$TELEGRAM_BOT_TOKEN|g" "$CONFIG_FILE"
    echo "✓ Substituted TELEGRAM_BOT_TOKEN"
else
    echo "ℹ TELEGRAM_BOT_TOKEN not set (optional)"
fi

# Replace TELEGRAM_USER_ID (optional)
if [ ! -z "$TELEGRAM_USER_ID" ]; then
    # Add user ID to allowFrom array
    sed -i "s|\"allowFrom\": \[\]|\"allowFrom\": [\"$TELEGRAM_USER_ID\"]|g" "$CONFIG_FILE"
    echo "✓ Added TELEGRAM_USER_ID to allowFrom"
else
    echo "ℹ TELEGRAM_USER_ID not set (optional)"
fi

echo "=========================================="
echo "Configuration initialized successfully!"
echo "=========================================="

# Show final config (with API keys masked)
echo "Final configuration:"
cat "$CONFIG_FILE" | sed 's/sk-[a-zA-Z0-9-]*/sk-***MASKED***/g'

echo "=========================================="
echo "Starting nanobot..."
echo "=========================================="

# Execute nanobot with all arguments
exec nanobot "$@"

# Made with Bob
