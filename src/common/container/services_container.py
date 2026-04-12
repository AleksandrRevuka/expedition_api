"""
Services container.

password_service and token_service are registered here.
"""

from dependency_injector import containers, providers

from src.modules.users.infrastructure.password_service import PasswordService
from src.modules.users.infrastructure.token_service import TokenService


class ServicesContainer(containers.DeclarativeContainer):
    uows = providers.DependenciesContainer()

    password_service = providers.Singleton(PasswordService)
    token_service = providers.Singleton(TokenService)
