from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
import traceback

class ExceptionInfo(BaseModel):
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

class SafeErrorMixin(BaseModel):
    """ Mixin for Error Field """
    error: Optional[ExceptionInfo] = Field(default=None)
    
    @field_validator('error', mode='before')
    @classmethod
    def validate_error(cls, v: Any) -> Optional[ExceptionInfo]:
        """Convert Exception objects to ExceptionInfo during validation"""
        if isinstance(v, BaseException):
            return ExceptionInfo.from_exception(v)
        return v