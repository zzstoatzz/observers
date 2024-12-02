# observers

minimal notification observer tools for claude

## setup

```bash
# clone this repo
gh repo clone zzstoatzz/observers
cd observers

# install dependencies
uv venv
uv sync

# configure env
cat > .env << EOF
GITHUB_TOKEN=your-token
GITHUB_ENABLED=true
EOF

# setup for Claude Desktop
uv run fastmcp install start.py -f .env
```