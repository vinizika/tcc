from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.base_exception import BaseAppException
from app.schemas.error import ErrorResponse


async def app_exception_handler(
    request: Request,
    exc: BaseAppException,
):

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.__class__.__name__,
            message=exc.message,
        ).model_dump(),
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "Erro interno do servidor.",
        },
    )