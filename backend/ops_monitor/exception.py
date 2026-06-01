from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class ChatbotException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def handle_exception(request: Request, exc: ChatbotException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
