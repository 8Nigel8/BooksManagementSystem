from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.exc import IntegrityError

from app.exceptions.not_found import BookNotFound


async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response

    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Invalid or expired token"}
        )

    except IntegrityError:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Database integrity error"}
        )

    except BookNotFound as e:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": str(e)}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Internal server error{str(e)}"}
        )
