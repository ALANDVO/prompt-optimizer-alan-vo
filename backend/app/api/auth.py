from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.security import (
    create_demo_token,
    get_current_user,
    UserPrincipal,
)
from app.models.schemas import (
    DemoLoginRequest,
    TokenResponse,
    UserProfileResponse,
    OIDCConfigResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/config", response_model=OIDCConfigResponse)
def get_oidc_configuration() -> OIDCConfigResponse:
    return OIDCConfigResponse(
        issuer_url=settings.oidc_issuer_url,
        client_id=settings.oidc_client_id,
        audience=settings.oidc_audience,
        demo_mode=settings.demo_mode,
        environment=settings.environment,
    )


@router.post("/demo-login", response_model=TokenResponse)
def demo_login(req: DemoLoginRequest) -> TokenResponse:
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo login is disabled on this server. Please use Keycloak OIDC.",
        )
    token = create_demo_token(req.username, req.role)
    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=43200,
        user_id=f"demo-user-{req.username}",
        username=req.username,
        roles=[req.role],
    )


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: UserPrincipal = Depends(get_current_user),
) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        roles=current_user.roles,
        is_demo=current_user.is_demo,
    )


@router.post("/logout")
def logout(current_user: UserPrincipal = Depends(get_current_user)) -> dict[str, str]:
    return {"status": "logged_out", "message": "Session invalidated."}
