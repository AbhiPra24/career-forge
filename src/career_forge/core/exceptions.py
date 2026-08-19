"""
Typed exception classes for CareerForge
"""


class CareerForgeError(Exception):
    """Base exception for all CareerForge errors."""
    pass


class ParserError(CareerForgeError):
    """Raised when parsing a resume or job document fails."""
    pass


class CompilationError(CareerForgeError):
    """Raised when LaTeX compilation to PDF fails."""
    pass


class DeliverabilityError(CareerForgeError):
    """Raised when email deliverability validation fails."""
    pass


class RateLimitError(CareerForgeError):
    """Raised when API quota or credit limit is exceeded."""
    pass


class DatabaseError(CareerForgeError):
    """Raised when database or cache operation fails."""
    pass
