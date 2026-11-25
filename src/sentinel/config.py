"""Configuração centralizada do ManyGym Sentinel.

Todas as variáveis de ambiente são lidas aqui. Os valores sensíveis nunca
são impressos: o token não aparece na representação dos objetos de
configuração nem nas mensagens de erro.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping


class ConfigError(ValueError):
    """Configuração obrigatória em falta ou inválida."""


@dataclass(frozen=True)
class GithubConfig:
    """Configuração necessária para comunicar com o GitHub."""

    token: str = field(repr=False)
    repos: tuple[str, ...]


@dataclass(frozen=True)
class Config:
    """Configuração da aplicação.

    Os campos de integrações ainda não implementadas são opcionais. A
    validação só acontece quando o módulo correspondente a pede.
    """

    github_token: str | None = field(default=None, repr=False)
    github_repos: tuple[str, ...] = ()

    def require_github(self) -> GithubConfig:
        """Devolver a configuração do GitHub ou falhar se estiver incompleta."""
        missing = []
        if not self.github_token:
            missing.append("GITHUB_TOKEN")
        if not self.github_repos:
            missing.append("GITHUB_REPOS")
        if missing:
            raise ConfigError(
                "Variáveis de ambiente obrigatórias em falta: " + ", ".join(missing)
            )

        invalid = [repo for repo in self.github_repos if not _is_valid_repo(repo)]
        if invalid:
            raise ConfigError(
                "GITHUB_REPOS deve usar o formato 'owner/name': " + ", ".join(invalid)
            )

        return GithubConfig(token=self.github_token, repos=self.github_repos)


def load_config(environ: Mapping[str, str] | None = None) -> Config:
    """Ler a configuração a partir do ambiente, sem validar integrações.

    Recebe um mapeamento opcional para permitir testes sem credenciais reais.
    """
    env = os.environ if environ is None else environ
    return Config(
        github_token=_optional(env.get("GITHUB_TOKEN")),
        github_repos=_parse_repos(env.get("GITHUB_REPOS")),
    )


def _optional(value: str | None) -> str | None:
    """Normalizar um valor opcional, tratando espaços vazios como ausência."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_repos(value: str | None) -> tuple[str, ...]:
    """Converter a lista separada por vírgulas numa sequência limpa."""
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _is_valid_repo(repo: str) -> bool:
    """Verificar o formato estrutural 'owner/name'."""
    owner, separator, name = repo.partition("/")
    if not separator or not owner or not name:
        return False
    if "/" in name:
        return False
    if any(character.isspace() for character in repo):
        return False
    return True
