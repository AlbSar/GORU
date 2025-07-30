"""
Kullanıcı ve kimlik doğrulama endpoint'leri.
ERP sistemi için kullanıcı yönetimi CRUD işlemlerini sağlar.
"""

from typing import List

from app.auth import get_current_user
from app.core.security import create_access_token, hash_password
from app.routes.common import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models, schemas

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.get("/test/")
async def test_endpoint():
    """Test endpoint"""
    return {"detail": "Test endpoint çalışıyor!"}


@router.post(
    "/login/",
    summary="Kullanıcı girişi / User login",
    responses={
        200: {"description": "Başarılı giriş / Successful login"},
        401: {"description": "Geçersiz kimlik bilgileri / Invalid credentials"},
    },
)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    TR: Kullanıcı girişi yapar ve JWT token döndürür.
    EN: Performs user login and returns JWT token.
    """
    # Test için basit bir kullanıcı kontrolü
    # Gerçek uygulamada database'den kullanıcı kontrolü yapılır
    if login_data.username == "admin" and login_data.password == "admin123":
        # Token oluştur
        access_token = create_access_token(
            data={"sub": login_data.username, "role": "admin"}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": login_data.username,
                "role": "admin",
                "permissions": ["read", "write", "delete", "admin"],
            },
        }
    elif login_data.username == "user" and login_data.password == "user123":
        # Normal kullanıcı token'ı
        access_token = create_access_token(
            data={"sub": login_data.username, "role": "user"}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": login_data.username,
                "role": "user",
                "permissions": ["read", "write"],
            },
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı adı veya şifre / Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Kullanıcı oluştur / Create user",
    responses={
        201: {
            "description": "Kullanıcı başarıyla oluşturuldu / "
            "User created successfully."
        },
        400: {
            "description": "E-posta zaten kayıtlı veya geçersiz veri / "
            "Email already registered or invalid data."
        },
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    user_auth=Depends(get_current_user),
):
    """
    TR: Yeni kullanıcı oluşturur. E-posta benzersiz olmalıdır.
    EN: Creates a new user. Email must be unique.
    """
    print(f"[DEBUG] Gelen kullanıcı verisi: {user.model_dump()}")
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        print(f"[DEBUG] E-posta zaten kayıtlı: {user.email}")
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )
    try:
        hashed_pw = hash_password(user.password)
        user_data = user.model_dump(exclude={"password"})
        if "is_active" in user_data:
            user_data["is_active"] = int(user_data["is_active"])
        db_user = models.User(**user_data, password_hash=hashed_pw)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print(f"[DEBUG] Kullanıcı başarıyla oluşturuldu: {db_user.id}")
        return db_user
    except Exception as e:
        print(f"[ERROR] Kullanıcı oluşturulurken hata: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=List[schemas.UserRead],
    summary="Kullanıcıları listele / List users",
    responses={
        200: {"description": "Kullanıcı listesi / List of users."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
async def list_users(
    db: Session = Depends(get_db), user_auth=Depends(get_current_user)
):
    """
    TR: Tüm kullanıcıları listeler.
    EN: Lists all users.
    """
    return db.query(models.User).all()


@router.get(
    "/{user_id}",
    response_model=schemas.UserRead,
    summary="Kullanıcı detay / User detail",
    responses={
        200: {"description": "Kullanıcı ve siparişleri / User and their orders."},
        404: {"description": "Kullanıcı bulunamadı / User not found."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_auth=Depends(get_current_user),
):
    """
    TR: Kullanıcıyı ve siparişlerini getirir.
    EN: Returns user and their orders.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Kullanıcı bulunamadı. / User not found."
        )
    return user


@router.put(
    "/{user_id}",
    response_model=schemas.UserRead,
    summary="Kullanıcı güncelle / Update user",
    responses={
        200: {"description": "Kullanıcı güncellendi / User updated."},
        404: {"description": "Kullanıcı bulunamadı / User not found."},
        400: {"description": "Geçersiz veri / Invalid data."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
async def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    user_auth=Depends(get_current_user),
):
    """
    TR: Kullanıcı bilgilerini günceller.
    EN: Updates user information.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=404, detail="Kullanıcı bulunamadı. / User not found."
        )
    update_data = user.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = int(update_data["is_active"])
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kullanıcı sil / Delete user",
    responses={
        204: {"description": "Kullanıcı silindi / User deleted."},
        404: {"description": "Kullanıcı bulunamadı / User not found."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_auth=Depends(get_current_user),
):
    """
    TR: Kullanıcıyı siler.
    EN: Deletes a user.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=404, detail="Kullanıcı bulunamadı. / User not found."
        )
    db.delete(db_user)
    db.commit()
    return
