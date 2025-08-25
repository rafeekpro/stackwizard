"""
Token Rotation Service
Implements secure refresh token rotation mechanism
"""
import secrets
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.services.auth import AuthService

logger = logging.getLogger(__name__)


class RefreshTokenStore:
    """
    Store for managing refresh tokens
    In production, this should use Redis or a database table
    """
    
    def __init__(self):
        # In-memory storage (replace with Redis/DB in production)
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.user_tokens: Dict[str, set] = {}  # Track tokens per user
    
    async def store_token(
        self,
        token_hash: str,
        user_id: str,
        family_id: str,
        expires_at: datetime,
        metadata: Optional[Dict] = None
    ):
        """Store refresh token with metadata"""
        self.tokens[token_hash] = {
            "user_id": user_id,
            "family_id": family_id,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
            "used": False,
            "metadata": metadata or {}
        }
        
        # Track user tokens
        if user_id not in self.user_tokens:
            self.user_tokens[user_id] = set()
        self.user_tokens[user_id].add(token_hash)
        
        # Cleanup expired tokens
        await self._cleanup_expired_tokens()
    
    async def get_token(self, token_hash: str) -> Optional[Dict[str, Any]]:
        """Get token data by hash"""
        token_data = self.tokens.get(token_hash)
        
        if token_data:
            # Check if expired
            if datetime.now(timezone.utc) > token_data["expires_at"]:
                await self.revoke_token(token_hash)
                return None
        
        return token_data
    
    async def mark_token_used(self, token_hash: str):
        """Mark token as used"""
        if token_hash in self.tokens:
            self.tokens[token_hash]["used"] = True
            self.tokens[token_hash]["used_at"] = datetime.now(timezone.utc)
    
    async def revoke_token(self, token_hash: str):
        """Revoke a single token"""
        token_data = self.tokens.get(token_hash)
        if token_data:
            user_id = token_data["user_id"]
            del self.tokens[token_hash]
            
            if user_id in self.user_tokens:
                self.user_tokens[user_id].discard(token_hash)
    
    async def revoke_token_family(self, family_id: str):
        """Revoke all tokens in a family (for security breach)"""
        tokens_to_revoke = []
        
        for token_hash, token_data in self.tokens.items():
            if token_data["family_id"] == family_id:
                tokens_to_revoke.append(token_hash)
        
        for token_hash in tokens_to_revoke:
            await self.revoke_token(token_hash)
        
        logger.warning(f"Revoked token family {family_id} due to potential breach")
    
    async def revoke_user_tokens(self, user_id: str):
        """Revoke all tokens for a user"""
        if user_id in self.user_tokens:
            tokens_to_revoke = list(self.user_tokens[user_id])
            for token_hash in tokens_to_revoke:
                await self.revoke_token(token_hash)
            
            del self.user_tokens[user_id]
    
    async def _cleanup_expired_tokens(self):
        """Remove expired tokens from storage"""
        current_time = datetime.now(timezone.utc)
        expired_tokens = []
        
        for token_hash, token_data in self.tokens.items():
            if current_time > token_data["expires_at"]:
                expired_tokens.append(token_hash)
        
        for token_hash in expired_tokens:
            await self.revoke_token(token_hash)


class TokenRotationService:
    """
    Service for handling refresh token rotation
    Implements security best practices for token management
    """
    
    def __init__(self):
        self.auth_service = AuthService()
        self.token_store = RefreshTokenStore()
    
    def _hash_token(self, token: str) -> str:
        """Create secure hash of token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _generate_family_id(self) -> str:
        """Generate unique family ID for token chain"""
        return secrets.token_urlsafe(32)
    
    async def create_token_pair(
        self,
        user: User,
        db: AsyncSession,
        metadata: Optional[Dict] = None
    ) -> Tuple[str, str, str]:
        """
        Create new access and refresh token pair
        
        Returns:
            Tuple of (access_token, refresh_token, family_id)
        """
        # Generate family ID for this token chain
        family_id = self._generate_family_id()
        
        # Create access token
        access_token = self.auth_service.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            scopes=["admin"] if user.is_superuser else ["user"]
        )
        
        # Create refresh token with family ID
        refresh_token_data = {
            "sub": str(user.id),
            "family_id": family_id,
            "jti": secrets.token_urlsafe(32),  # Unique token ID
        }
        
        refresh_token = jwt.encode(
            {
                **refresh_token_data,
                "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                "type": "refresh"
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Store refresh token
        token_hash = self._hash_token(refresh_token)
        await self.token_store.store_token(
            token_hash=token_hash,
            user_id=str(user.id),
            family_id=family_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            metadata=metadata
        )
        
        # Update user last login
        user.last_login_at = datetime.now(timezone.utc)
        user.login_count = (user.login_count or 0) + 1
        await db.commit()
        
        logger.info(f"Created new token pair for user {user.id} with family {family_id}")
        
        return access_token, refresh_token, family_id
    
    async def rotate_refresh_token(
        self,
        refresh_token: str,
        db: AsyncSession
    ) -> Tuple[str, str]:
        """
        Rotate refresh token - issue new token pair and invalidate old token
        
        Returns:
            Tuple of (new_access_token, new_refresh_token)
        """
        try:
            # Decode the refresh token
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Verify token type
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            family_id = payload.get("family_id")
            
            if not user_id or not family_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Check if token exists and is valid
            token_hash = self._hash_token(refresh_token)
            token_data = await self.token_store.get_token(token_hash)
            
            if not token_data:
                # Token not found - possible theft, revoke entire family
                await self.token_store.revoke_token_family(family_id)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not found or expired. All tokens revoked for security."
                )
            
            # Check if token was already used (replay attack detection)
            if token_data.get("used"):
                # Token reuse detected - revoke entire family
                await self.token_store.revoke_token_family(family_id)
                logger.warning(f"Token reuse detected for user {user_id}, family {family_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token reuse detected. All tokens revoked for security."
                )
            
            # Mark old token as used
            await self.token_store.mark_token_used(token_hash)
            
            # Get user
            result = await db.execute(
                select(User).where(User.id == UUID(user_id))
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                await self.token_store.revoke_token_family(family_id)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new token pair with same family ID
            access_token = self.auth_service.create_access_token(
                data={"sub": str(user.id), "email": user.email},
                scopes=["admin"] if user.is_superuser else ["user"]
            )
            
            # Create new refresh token with same family ID
            new_refresh_token_data = {
                "sub": str(user.id),
                "family_id": family_id,  # Keep same family ID
                "jti": secrets.token_urlsafe(32),
                "parent_jti": payload.get("jti"),  # Reference to parent token
            }
            
            new_refresh_token = jwt.encode(
                {
                    **new_refresh_token_data,
                    "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                    "type": "refresh"
                },
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )
            
            # Store new refresh token
            new_token_hash = self._hash_token(new_refresh_token)
            await self.token_store.store_token(
                token_hash=new_token_hash,
                user_id=str(user.id),
                family_id=family_id,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                metadata={"rotated_from": token_hash}
            )
            
            # Revoke old token
            await self.token_store.revoke_token(token_hash)
            
            logger.info(f"Rotated refresh token for user {user.id}, family {family_id}")
            
            return access_token, new_refresh_token
            
        except JWTError as e:
            logger.error(f"JWT error during token rotation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        except Exception as e:
            logger.error(f"Error during token rotation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error during token rotation"
            )
    
    async def revoke_refresh_token(
        self,
        refresh_token: str,
        revoke_family: bool = False
    ):
        """
        Revoke a refresh token
        
        Args:
            refresh_token: The token to revoke
            revoke_family: If True, revoke entire token family
        """
        try:
            # Decode token to get family ID
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            family_id = payload.get("family_id")
            token_hash = self._hash_token(refresh_token)
            
            if revoke_family and family_id:
                await self.token_store.revoke_token_family(family_id)
            else:
                await self.token_store.revoke_token(token_hash)
            
            logger.info(f"Revoked refresh token {'family' if revoke_family else ''}")
            
        except JWTError:
            # Token invalid or expired, ignore
            pass
    
    async def revoke_all_user_tokens(self, user_id: str, db: AsyncSession):
        """
        Revoke all refresh tokens for a user
        Used for logout from all devices or security breach
        """
        await self.token_store.revoke_user_tokens(user_id)
        logger.info(f"Revoked all tokens for user {user_id}")
    
    async def validate_refresh_token(self, refresh_token: str) -> bool:
        """
        Validate if refresh token is valid and not revoked
        """
        try:
            # Decode token
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                return False
            
            # Check if token exists in store
            token_hash = self._hash_token(refresh_token)
            token_data = await self.token_store.get_token(token_hash)
            
            return token_data is not None and not token_data.get("used", False)
            
        except JWTError:
            return False
    
    async def get_active_sessions(self, user_id: str) -> list:
        """
        Get list of active sessions (refresh tokens) for a user
        """
        sessions = []
        
        if user_id in self.token_store.user_tokens:
            for token_hash in self.token_store.user_tokens[user_id]:
                token_data = self.token_store.tokens.get(token_hash)
                if token_data and not token_data.get("used"):
                    sessions.append({
                        "created_at": token_data["created_at"],
                        "expires_at": token_data["expires_at"],
                        "family_id": token_data["family_id"],
                        "metadata": token_data.get("metadata", {})
                    })
        
        return sessions


# Global instance
token_rotation_service = TokenRotationService()