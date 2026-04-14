from src.modules.users.infrastructure.units_of_work import UsersStorageUnitOfWork

from fastapi import Request
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import NameEmail
from taskiq import TaskiqDepends

from src.common.container.main_container import Container
from src.conf.email_config import get_mail_conf
from src.conf.enums import Role
from src.tkq import broker


def get_container(request: Request = TaskiqDepends()) -> Container:
    return request.app.container


def get_uow_user(container: Container = TaskiqDepends(get_container)) -> UsersStorageUnitOfWork:
    return container.uows.users_storage_uow()

@broker.task
async def send_welcome_email_task(email: str, name: str) -> None:
    fm = FastMail(get_mail_conf())
    message = MessageSchema(
        subject="Welcome to Expedition!",
        recipients=[NameEmail(name=name, email=email)],
        template_body={"name": name},
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="welcome.html")


@broker.task
async def change_role_task(
    user_id: str,
    role: Role,
    uow: UsersStorageUnitOfWork = TaskiqDepends(get_uow_user)
) -> None:

    async with uow:
        exists_user = await uow.users.get_one(id=user_id)
        if exists_user is not None:
            exists_user.change_role(role=role)
            await uow.users.update_one(exists_user)
            await uow.commit()
