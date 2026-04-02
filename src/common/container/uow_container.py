"""
Unit-of-Work container.

UoW providers are added to this file as modules land:
  - users:       users_storage_uow  (UsersStorageUnitOfWork)
  - expeditions: expeditions_storage_uow  (ExpeditionsStorageUnitOfWork)
  - members:     members_storage_uow  (MembersStorageUnitOfWork)
"""

from dependency_injector import containers, providers


class UowContainer(containers.DeclarativeContainer):
    base_container = providers.DependenciesContainer()

    # Providers added here once modules exist:
    # users_storage_uow = providers.Factory(
    #     UsersStorageUnitOfWork,
    #     session_factory=base_container.db_manager.provided.session_factory,
    # )
