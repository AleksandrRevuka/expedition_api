"""
Unit-of-Work container.
"""

from dependency_injector import containers, providers

from src.modules.users.infrastructure.units_of_work import UsersStorageUnitOfWork
from src.modules.expeditions.infrastructure.units_of_work import (
    ExpeditionsStorageUnitOfWork,
)


class UowContainer(containers.DeclarativeContainer):
    base_container = providers.DependenciesContainer()

    users_storage_uow = providers.Factory(
        UsersStorageUnitOfWork,
        session_factory=base_container.db_manager.provided.session_factory,
    )

    expeditions_storage_uow = providers.Factory(
        ExpeditionsStorageUnitOfWork,
        session_factory=base_container.db_manager.provided.session_factory,
    )
