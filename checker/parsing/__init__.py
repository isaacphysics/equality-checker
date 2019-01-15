
__all__ = ["UnsafeInputException", "ParsingException"]


class ParsingException(ValueError):
    """An exception to be raised when parsing fails."""
    pass


class UnsafeInputException(ValueError):
    """An exception to be raised when unexpected input is provided."""
    pass