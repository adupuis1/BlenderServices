from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.auth import Caller, InvalidToken, caller_from_token
from common.db import SessionDep

bearer = HTTPBearer(auto_error=False)

def current_caller(
        creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Caller:
    if creds is None:
        raise HTTPException(401, "missing bearer token")
    try:
        return caller_from_token(creds.credentials)
    except InvalidToken as exc:
        raise HTTPException(401, str(exc)) from exc

CurrentCaller = Annotated[Caller, Depends(current_caller)]

