from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from common.auth import Caller, InvalidToken, caller_from_token
from common.config import settings

oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/login/access-token"
)

def current_caller(token: Annotated[str, Depends(oauth2)]) -> Caller:
    try:
        return caller_from_token(token)
    except InvalidToken as exc:
        raise HTTPException(401, str(exc), headers={"WWW-Authenticate": "Bearer"}) from exc

CurrentCaller = Annotated[Caller, Depends(current_caller)]