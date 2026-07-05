# AGENTS.md

## Cursor Cloud specific instructions

As of this writing, this repository is a **vision/spec-only repository**. It contains
only `README.md` (the PEGASO concept document) and `LICENSE`.

There is currently:

- No source code in any language.
- No package manifest or lockfile (e.g. `package.json`, `pyproject.toml`,
  `requirements.txt`, `go.mod`, `Cargo.toml`).
- No build, test, or lint tooling, scripts, `Makefile`, or task runner.
- No `Dockerfile`, `docker-compose`, devcontainer, `.cursor/environment.json`, or CI config.
- No runnable service or application.

Implications for environment setup:

- There is nothing to install, build, run, test, or lint yet, so no update/bootstrap
  script is needed. Any such script would be a no-op until an implementation and a
  package manifest are added.
- Once code and a package manifest/lockfile are introduced, update this section with
  the real setup, run, test, and lint commands and (if useful) configure a minimal
  dependency-refresh update script for future cloud agents.
