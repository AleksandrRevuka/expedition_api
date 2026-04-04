class ExpeditionNotFoundError(Exception):
    """
    Exception raised when an expedition is not found.
    """

    def __init__(self, message: str = "Expedition not found"):
        super().__init__(message)
        self.message = message


class ExpeditionAccessDeniedError(Exception):
    """
    Exception raised when a user is not allowed to access an expedition.
    """

    def __init__(self, message: str = "Access denied"):
        super().__init__(message)
        self.message = message


class InvalidStatusTransitionError(Exception):
    """
    Exception raised when a status transition is invalid.
    """

    def __init__(self, message: str = "Invalid status transition"):
        super().__init__(message)
        self.message = message


class MemberAlreadyInvitedError(Exception):
    """
    Exception raised when a user is already invited to an expedition.
    """

    def __init__(self, message: str = "User is already a member of this expedition"):
        super().__init__(message)
        self.message = message


class MemberNotFoundError(Exception):
    """
    Exception raised when a member is not found.
    """

    def __init__(self, message: str = "Member not found"):
        super().__init__(message)
        self.message = message


class InvalidExpeditionStateError(Exception):
    """Invalid status transition."""

    def __init__(self, message: str = "Invalid status transition"):
        super().__init__(message)
        self.message = message


class ExpeditionStartTooEarlyError(Exception):
    """Expedition cannot start before start_at."""

    def __init__(self, message: str = "Expedition cannot start before start_at"):
        super().__init__(message)
        self.message = message


class NotEnoughConfirmedMembersError(Exception):
    """Not enough confirmed members."""

    def __init__(self, message: str = "At least 2 confirmed members required"):
        super().__init__(message)
        self.message = message


class ExpeditionCapacityExceededError(Exception):
    """Too many confirmed members."""

    def __init__(self, message: str = "Capacity exceeded"):
        super().__init__(message)
        self.message = message


class MemberAlreadyInActiveExpeditionError(Exception):
    """Member already participates in another active expedition."""

    def __init__(self, message: str = "Member already in another active expedition"):
        super().__init__(message)
        self.message = message


class MemberConfirmAccessDeniedError(Exception):
    """User is not allowed to confirm this membership."""

    def __init__(self, message: str = "Only invited user can confirm this membership"):
        super().__init__(message)
        self.message = message


class InvalidMemberStateTransitionError(Exception):
    """Invalid state transition for expedition member."""

    def __init__(self, message: str = "Cannot confirm member"):
        super().__init__(message)
        self.message = message


class InvalidExpeditionMemberRoleError(Exception):
    """Invalid role for expedition member."""

    def __init__(self, message: str = "Invalid role for expedition member"):
        super().__init__(message)
        self.message = message
