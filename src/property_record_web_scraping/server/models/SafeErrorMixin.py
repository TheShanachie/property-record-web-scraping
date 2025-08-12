from pydantic import BaseModel, Field, field_validator
from .SanitizeMixin import SanitizedBaseModel
from typing import Optional, Any
import traceback

class ExceptionInfo(SanitizedBaseModel):
    type: str
    message: str
    file: Optional[str]
    line: Optional[int]
    trace: Optional[str]

    @classmethod
    def from_exception(cls, exc: Exception) -> "ExceptionInfo":
        tb = exc.__traceback__
        trace_str = ''.join(traceback.format_exception(type(exc), exc, tb)) if tb else None

        return cls(
            type=type(exc).__name__,
            message=str(exc),
            file=tb.tb_frame.f_code.co_filename if tb else None,
            line=tb.tb_lineno if tb else None,
            trace=trace_str
        )

    def format_details(self) -> str:
        """Return a nicely formatted string of the exception details."""
        details = [
            f"Type   : {self.type}",
            f"Message: {self.message}",
            f"File   : {self.file}" if self.file else "File   : <unknown>",
            f"Line   : {self.line}" if self.line else "Line   : <unknown>",
            "Traceback:",
            f"{self.trace.strip()}" if self.trace else "  <no traceback available>"
        ]
        return "\n    ".join(details)

    def __str__(self) -> str:
        return self.format_details()

    def __repr__(self) -> str:
        return self.format_details()

class SafeErrorMixin(SanitizedBaseModel):
    """ Mixin for Error Field """
    error: Optional[ExceptionInfo] = Field(default=None)
    
    @field_validator('error', mode='before')
    @classmethod
    def validate_error(cls, v: Any) -> Optional[ExceptionInfo]:
        """Convert Exception objects to ExceptionInfo during validation"""
        if isinstance(v, BaseException):
            return ExceptionInfo.from_exception(v)
        return v