# Chat UI Prototype — Streamlit and FastAPI

An earlier chat-interface experiment with a Streamlit UI, FastAPI registration/login backend, and MySQL models.

**Status:** prototype. The active chat/search path returns mock responses and keeps conversation history in process memory. It is not a working LLM or search application.

## Purpose and contents

This repository preserves work on chat layout, sidebar/search controls, authentication screens, and frontend API calls. The later [GPTCraft project](https://github.com/Nitsh-kumar/GPT_craft) has a real inference path and persisted conversations.

- [frontend/main.py](frontend/main.py): Streamlit application.
- [frontend/components](frontend/components): chat/sidebar components.
- [Backend/app/main.py](Backend/app/main.py): API registration and startup.
- [Backend/app/api/v1/endpoints/chat.py](Backend/app/api/v1/endpoints/chat.py): active mock chat and in-memory state.
- [Backend/app/models](Backend/app/models): user and conversation models/helpers.

## Before running

The supplied source review identified committed configuration credentials, default-account seeding/logging, and missing ownership checks on chat/history routes. Revoke any issued credentials and sanitize startup/configuration before running this outside an isolated development environment. Ignore rules do not remove already tracked auth configuration.

## Local development layout

The two dependency files serve different parts of the prototype:

```bash
# From repository root, inside an activated Python virtual environment
python -m pip install -r Backend/requirements.txt
python -m pip install -r Requirement.txt
```

Inspect backend settings and provision an isolated MySQL database with your own local configuration. The current source defaults are not a safe deployment configuration.

Once those issues are addressed:

```bash
# Terminal 1, from Backend/
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
# Terminal 2, from repository root
python -m streamlit run frontend/main.py
```

The startup scripts are also present, but the backend script binds to all interfaces. Prefer loopback for a local experiment. Inspect `/docs` after successful startup for the current API paths rather than relying on old endpoint examples.

## Limitations and direction

Mock replies do not demonstrate provider integration. Global in-memory chat dictionaries do not provide durable or isolated multi-worker storage. Authenticated ownership must be enforced on each history/read/delete route.

Compare useful UI work with GPTCraft before any consolidation. Preserve unique behavior and check existing consumers before retiring this prototype. No new license is granted by this documentation update.

See [project status](docs/PROJECT_STATUS.md).

## Validation

This documentation was checked against repository files on 13 October 2026. Builds, application runs, and test suites were not executed during this documentation pass. Commands below describe the intended local workflow, not a verified deployment.
