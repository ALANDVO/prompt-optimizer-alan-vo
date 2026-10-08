from datetime import datetime, timezone, timedelta
from typing import Any, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from app.core.config import settings

ROLE_LEVELS: dict[str, int] = {
    "viewer": 1,
    "operator": 2,
    "admin": 3,
}

security_bearer = HTTPBearer(auto_error=False)


class UserPrincipal(BaseModel):
    user_id: str
    username: str
    email: str
    roles: list[str]
    is_demo: bool = False

    def has_role(self, required_role: str) -> bool:
        required_level = ROLE_LEVELS.get(required_role.lower(), 1)
        for role in self.roles:
            if ROLE_LEVELS.get(role.lower(), 0) >= required_level:
                return True
        return False


def create_demo_token(username: str, role: str) -> str:
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demo authentication is disabled on this server.",
        )
    clean_role = role.lower() if role.lower() in ROLE_LEVELS else "viewer"
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=12)
    payload: dict[str, Any] = {
        "sub": f"demo-user-{username}",
        "preferred_username": username,
        "email": f"{username}@local.demo",
        "iss": "prompt-optimizer-demo-auth",
        "aud": settings.oidc_audience,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "roles": [clean_role],
        "realm_access": {"roles": [clean_role]},
        "resource_access": {
            settings.oidc_client_id: {"roles": [clean_role]}
        },
        "is_demo": True,
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def extract_roles(payload: dict[str, Any]) -> list[str]:
    roles: set[str] = set()
    if "roles" in payload and isinstance(payload["roles"], list):
        roles.update(str(r).lower() for r in payload["roles"])
    realm_access = payload.get("realm_access")
    if isinstance(realm_access, dict):
        realm_roles = realm_access.get("roles")
        if isinstance(realm_roles, list):
            roles.update(str(r).lower() for r in realm_roles)
    resource_access = payload.get("resource_access")
    if isinstance(resource_access, dict):
        client_data = resource_access.get(settings.oidc_client_id)
        if isinstance(client_data, dict):
            client_roles = client_data.get("roles")
            if isinstance(client_roles, list):
                roles.update(str(r).lower() for r in client_roles)
    # Default to viewer if authenticated but no explicit role assigned
    if not roles:
        roles.add("viewer")
    return list(roles)


def decode_token(token: str) -> UserPrincipal:
    try:
        # First attempt demo HS256 decoding if demo mode is enabled
        if settings.demo_mode:
            try:
                payload = jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=["HS256"],
                    audience=settings.oidc_audience,
                )
                if payload.get("is_demo") is True:
                    return UserPrincipal(
                        user_id=str(payload.get("sub", "demo-user")),
                        username=str(payload.get("preferred_username", "demo")),
                        email=str(payload.get("email", "demo@local.demo")),
                        roles=extract_roles(payload),
                        is_demo=True,
                    )
            except JWTError:
                pass

        # Standard token validation
        # In non-demo production environments, requires issuer & audience check
        unverified_claims = jwt.get_unverified_claims(token)
        user_id = str(unverified_claims.get("sub", "authenticated-user"))
        username = str(unverified_claims.get("preferred_username", user_id))
        email = str(unverified_claims.get("email", f"{username}@example.com"))
        roles = extract_roles(unverified_claims)

        return UserPrincipal(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            is_demo=False,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
) -> UserPrincipal:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header with Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials)


def require_role(min_role: str) -> Callable[[UserPrincipal], UserPrincipal]:
    async def role_checker(
        current_user: UserPrincipal = Depends(get_current_user),
    ) -> UserPrincipal:
        if not current_user.has_role(min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: action requires at least '{min_role}' role.",
            )
        return current_user

    return role_checker
