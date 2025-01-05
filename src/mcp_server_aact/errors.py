import logging
from typing import Type, TypeVar, Callable, Any
from functools import wraps

logger = logging.getLogger('mcp_aact_server.errors')

class AACTError(Exception):
    """Base exception class for AACT server errors"""
    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error

class DatabaseError(AACTError):
    """Database-related errors"""
    pass

class ToolError(AACTError):
    """Tool execution errors"""
    pass

class ResourceError(AACTError):
    """Resource handling errors"""
    pass

T = TypeVar('T')

def handle_errors(
    error_class: Type[AACTError],
    error_message: str,
    log_level: int = logging.ERROR
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for standardized error handling.
    
    Args:
        error_class: The type of error to raise
        error_message: Template string for error message
        log_level: Logging level to use
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, AACTError):
                    raise e
                
                msg = error_message.format(error=str(e))
                logger.log(log_level, msg, exc_info=True)
                raise error_class(msg, original_error=e)
        return wrapper
    return decorator 