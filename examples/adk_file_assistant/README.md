# ADK File Assistant

A minimal [Google ADK](https://google.github.io/adk-docs/) agent that uses
PEGASO's `local_files` capability to explore and edit a sandboxed workspace.

See [docs/TUTORIAL.md](../../docs/TUTORIAL.md) for the full walkthrough.

## Quick start

```bash
pip install -e ".[adk]"
cp .env.example .env   # add your GOOGLE_API_KEY
adk web ../             # open from examples/ parent folder
```

Select **file_assistant** in the ADK web UI.
