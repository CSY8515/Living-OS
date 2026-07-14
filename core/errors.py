class CoreError(RuntimeError):
    """Base error for safe Living OS Core failures."""


class ConcurrencyError(CoreError):
    """The requested record version is no longer current."""


class CommandRejected(CoreError):
    """A command failed validation or policy checks."""


class MigrationError(CoreError):
    """A compatibility migration could not be completed safely."""
