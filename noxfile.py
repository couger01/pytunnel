from __future__ import annotations

import nox

PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14", "3.15"]

nox.options.default_venv_backend = "uv"
nox.options.sessions = ["lint", "typecheck", "docs", "changelog", "tests"]


@nox.session(python=PYTHONS)
def tests(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest", *session.posargs)


@nox.session
def lint(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "format", "--check", ".")
    session.run("ruff", "check", ".")


@nox.session(name="format")
def format_code(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "format", ".")
    session.run("ruff", "check", "--fix", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ty", "check", "src", "tests", "scripts")


@nox.session
def changelog(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("towncrier", "build", "--draft", "--version", "0.1.0")


@nox.session
def docs(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("sphinx-build", "-W", "--keep-going", "-b", "html", "docs", "docs/_build/html")


@nox.session(name="prek")
def prek_session(session: nox.Session) -> None:
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        "--frozen",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("prek", "run", "--all-files", *session.posargs)
