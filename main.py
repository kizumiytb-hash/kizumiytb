import os
import uuid
import random
import asyncio
import datetime
from typing import Optional, Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# --- Configs ---
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
SECRET_KEY = os.environ.get("SECRET_KEY", "changemefortsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours

# --- MongoDB ---
client = AsyncIOMotorClient(MONGO_URL)
db = client.forex_broker

# --- Auth ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- FastAPI app ---
app = FastAPI(title="Forex Broker API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- Utilitaires ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    return user

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["password_hash"]):
        return False
    if not user.get("is_active", True):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = await db.users.find_one({"user_id": token_data.user_id})
    if user is None:
        raise credentials_exception
    return user

# --- Routes Auth ---
@app.post("/register")
async def register(user: UserRegister):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)

    user_doc = {
        "user_id": user_id,
        "email": user.email,
        "password_hash": hashed_password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "is_active": True,
        "created_at": datetime.datetime.utcnow(),
    }
    await db.users.insert_one(user_doc)
    return {"message": "Utilisateur créé avec succès"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe invalide")
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["user_id"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_me(current_user = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "phone": current_user.get("phone"),
    }

# --- Price simulation ---
current_prices = {
    "EURUSD": {"bid": 1.0532, "ask": 1.0535, "base": 1.0533},
    "XAUUSD": {"bid": 2678.45, "ask": 2678.50, "base": 2678.47},
}

async def simulate_prices():
    while True:
        for symbol in current_prices:
            base = current_prices[symbol]["base"]
            vol = 0.0005 if symbol == "EURUSD" else 0.005
            change = random.uniform(-vol, vol)
            new_price = base * (1 + change)
            current_prices[symbol]["bid"] = round(new_price, 5 if symbol == "EURUSD" else 2)
            current_prices[symbol]["ask"] = round(new_price, 5 if symbol == "EURUSD" else 2)
            if random.random() < 0.1:
                current_prices[symbol]["base"] = new_price
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup():
    asyncio.create_task(simulate_prices())

@app.get("/")
async def home():
    return {"message": "Bienvenue sur l'API Forex Broker"}

# Exemple endpoint protégé (utilisateur connecté)
@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    return {"message": f"Hello {current_user['email']}, vous êtes authentifié."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
