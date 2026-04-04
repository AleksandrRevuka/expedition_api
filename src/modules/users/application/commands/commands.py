from src.common.interfaces.commands import AbstractCommand
from src.conf.enums import Role


class CreateUserCommand(AbstractCommand):
    email: str
    password: str
    first_name: str
    last_name: str
    role: Role = Role.member


class LoginUserCommand(AbstractCommand):
    email: str
    password: str
