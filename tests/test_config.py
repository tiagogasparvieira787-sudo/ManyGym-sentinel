"""Testes da configuração centralizada."""

import pytest

from sentinel.config import ConfigError, load_config


def test_load_config_without_environment_variables():
    """A configuração pode ser carregada sem credenciais."""
    config = load_config({})

    assert config.github_token is None
    assert config.github_repos == ()

    with pytest.raises(ConfigError):
        config.require_github()


def test_load_config_parses_github_values():
    config = load_config(
        {
            "GITHUB_TOKEN": "  token-de-teste  ",
            "GITHUB_REPOS": " org/repo-one , org/repo-two,,",
        }
    )

    assert config.github_token == "token-de-teste"
    assert config.github_repos == ("org/repo-one", "org/repo-two")


def test_load_config_reads_process_environment(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token-do-ambiente")
    monkeypatch.setenv("GITHUB_REPOS", "org/repo")

    config = load_config()

    assert config.github_token == "token-do-ambiente"
    assert config.github_repos == ("org/repo",)


def test_require_github_returns_valid_configuration():
    config = load_config(
        {
            "GITHUB_TOKEN": "token-de-teste",
            "GITHUB_REPOS": "org/repo-one,org/repo-two",
        }
    )

    github = config.require_github()

    assert github.token == "token-de-teste"
    assert github.repos == ("org/repo-one", "org/repo-two")


def test_require_github_reports_missing_token():
    config = load_config({"GITHUB_REPOS": "org/repo"})

    with pytest.raises(ConfigError, match="GITHUB_TOKEN"):
        config.require_github()


def test_require_github_reports_missing_repos():
    config = load_config({"GITHUB_TOKEN": "token-de-teste"})

    with pytest.raises(ConfigError, match="GITHUB_REPOS"):
        config.require_github()


@pytest.mark.parametrize(
    "repo",
    [
        "repositorio-invalido",
        "/repo",
        "owner/",
        "owner/name/",
        "owner name/repo",
        "owner/repo name",
        "owner//repo",
    ],
)
def test_require_github_rejects_invalid_repo_format(repo):
    config = load_config({"GITHUB_TOKEN": "token-de-teste", "GITHUB_REPOS": repo})

    with pytest.raises(ConfigError, match="owner/name"):
        config.require_github()


def test_github_config_repr_does_not_expose_token():
    secret = "segredo-ficticio-do-github-config"
    github = load_config(
        {"GITHUB_TOKEN": secret, "GITHUB_REPOS": "org/repo"}
    ).require_github()

    assert secret not in repr(github)


def test_secret_is_not_exposed_in_representations_or_errors():
    secret = "segredo-ficticio-que-nao-deve-aparecer"
    config = load_config({"GITHUB_TOKEN": secret})

    assert secret not in repr(config)
    with pytest.raises(ConfigError) as excinfo:
        config.require_github()
    assert secret not in str(excinfo.value)
