import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import random
import math
from dotenv import load_dotenv

import stripe  # Stripe officiel

from auth import hash_password, verify_password, create_access_token, get_current_user, get_current_user_optional

# Charge les variables d'environnement UNE SEULE FOIS
load_dotenv()

# Récupère la clé Stripe et configure la lib Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
if not STRIPE_API_KEY:
    raise Exception("STRIPE_API_KEY environment variable is required")
stripe.api_key = STRIPE_API_KEY

# Initialise FastAPI UNE SEULE FOIS
app = FastAPI(title="Forex Broker API", version="2.0.0")

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Forex Broker"}

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.forex_broker

# Authentication Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    date_created: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    email_verified: bool = False

class User(BaseModel):
    user_id: str
    email: EmailStr
    password_hash: str
    profile: UserProfile
    created_at: datetime

# Trading Models
class Account(BaseModel):
    user_id: str
    account_id: str
    account_type: str  # 'demo' or 'real'
    balance: float
    equity: float
    margin: float
    free_margin: float
    currency: str = 'EUR'

class Order(BaseModel):
    user_id: str
    account_type: str
    symbol: str
    order_type: str  # 'buy' or 'sell'
    volume: float
    open_price: float
    leverage: int
    timestamp: Optional[datetime] = None
    status: str = 'open'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class Position(BaseModel):
    user_id: str
    account_type: str
    symbol: str
    order_type: str
    volume: float
    open_price: float
    current_price: float
    leverage: int
    profit_loss: float
    timestamp: datetime
    status: str = 'open'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class PriceData(BaseModel):
    symbol: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime

class Transaction(BaseModel):
    user_id: str
    account_type: str
    transaction_type: str  # 'stripe_deposit', 'stripe_withdrawal', 'recharge'
    amount: float
    status: str = 'completed'
    description: str
    payment_id: Optional[str] = None  # Stripe session ID or transfer ID
    timestamp: datetime

class PaymentTransaction(BaseModel):
    transaction_id: str
    user_id: str
    account_type: str
    amount: float
    currency: str
    session_id: str
    payment_status: str  # 'initiated', 'pending', 'paid', 'failed', 'expired'
    status: str  # 'initiated', 'pending', 'completed', 'failed', 'expired'
    metadata: Dict[str, str]
    timestamp: datetime

class TransactionRequest(BaseModel):
    account_type: str
    amount: float
    description: Optional[str] = ""

class DepositRequest(BaseModel):
    account_type: str
    amount: float

class WithdrawalRequest(BaseModel):
    account_type: str
    amount: float
    description: Optional[str] = ""

class RechargeRequest(BaseModel):
    account_type: str
    amount: float

# Payment packages for deposits - SECURITY: Defined on backend only
DEPOSIT_PACKAGES = {
    "small": 50.0,
    "medium": 100.0,
    "large": 200.0,
    "xlarge": 500.0,
    "custom": None  # Will allow custom amounts for specific requests
}

# Global price simulation
current_prices = {
    'EURUSD': {'bid': 1.0532, 'ask': 1.0532, 'base': 1.0532},
    'XAUUSD': {'bid': 2678.45, 'ask': 2678.45, 'base': 2678.45}
}

# Price simulation function
async def simulate_prices():
    while True:
        for symbol in current_prices:
            base_price = current_prices[symbol]['base']
            volatility = 0.0005 if symbol == 'EURUSD' else 0.005
            change = random.uniform(-volatility, volatility)
            new_price = base_price * (1 + change)
            current_prices[symbol]['bid'] = round(new_price, 5 if symbol == 'EURUSD' else 2)
            current_prices[symbol]['ask'] = round(new_price, 5 if symbol == 'EURUSD' else 2)
            if random.random() < 0.1:
                current_prices[symbol]['base'] = new_price
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_prices())

# Trading endpoints
@app.post("/api/orders")
async def place_order(order: Order, current_user = Depends(get_current_user)):
    # Override user_id from token for security
    order.user_id = current_user['user_id']
    
    symbol_prices = current_prices.get(order.symbol)
    if not symbol_prices:
        raise HTTPException(status_code=400, detail="Invalid symbol")
    
    open_price = symbol_prices['bid'] if order.order_type == 'sell' else symbol_prices['ask']
    
    if order.stop_loss:
        if order.order_type == 'buy' and order.stop_loss >= open_price:
            raise HTTPException(status_code=400, detail="Stop Loss must be below current price for BUY orders")
        elif order.order_type == 'sell' and order.stop_loss <= open_price:
            raise HTTPException(status_code=400, detail="Stop Loss must be above current price for SELL orders")
    
    if order.take_profit:
        if order.order_type == 'buy' and order.take_profit <= open_price:
            raise HTTPException(status_code=400, detail="Take Profit must be above current price for BUY orders")
        elif order.order_type == 'sell' and order.take_profit >= open_price:
            raise HTTPException(status_code=400, detail="Take Profit must be below current price for SELL orders")
    
    order_dict = order.dict()
    order_dict['order_id'] = str(uuid.uuid4())
    order_dict['open_price'] = open_price
    order_dict['timestamp'] = datetime.now()
    
    await db.orders.insert_one(order_dict)
    
    position = Position(
        user_id=current_user['user_id'],
        account_type=order.account_type,
        symbol=order.symbol,
        order_type=order.order_type,
        volume=order.volume,
        open_price=open_price,
        current_price=open_price,
        leverage=order.leverage,
        stop_loss=order.stop_loss,
        take_profit=order.take_profit,
        profit_loss=0.0,
        timestamp=datetime.now()
    )
    
    position_dict = position.dict()
    position_dict['position_id'] = str(uuid.uuid4())
    await db.positions.insert_one(position_dict)
    
    return {"order_id": order_dict['order_id'], "position_id": position_dict['position_id'], "status": "executed"}

@app.get("/api/positions/{account_type}")
async def get_positions(account_type: str, current_user = Depends(get_current_user)):
    positions = []
    async for position in db.positions.find({"user_id": current_user['user_id'], "account_type": account_type, "status": {"$ne": "closed"}}):
        symbol = position['symbol']
        current_price = current_prices[symbol]['bid']
        open_price = position['open_price']
        volume = position['volume']
        leverage = position['leverage']
        
        if position['order_type'] == 'buy':
            pips = current_price - open_price
        else:
            pips = open_price - current_price
        
        pip_value = 0.0001 if symbol == 'EURUSD' else 0.01
        profit_loss = (pips / pip_value) * volume * leverage * pip_value
        
        position['current_price'] = current_price
        position['profit_loss'] = round(profit_loss, 2)
        position['_id'] = str(position['_id'])
        positions.append(position)
    
    return positions

@app.delete("/api/positions/{position_id}")
async def close_position(position_id: str, current_user = Depends(get_current_user)):
    # Check if position belongs to current user
    position = await db.positions.find_one({"position_id": position_id, "user_id": current_user['user_id']})
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    current_price = current_prices[position['symbol']]['bid']
    
    result = await db.positions.update_one(
        {"position_id": position_id},
        {"$set": {
            "status": "closed",
            "close_reason": "Manual Close",
            "close_price": current_price,
            "closed_at": datetime.now()
        }}
    )
    
    if result.modified_count == 1:
        return {"status": "closed", "close_price": current_price}
    else:
        raise HTTPException(status_code=404, detail="Position not found")

@app.get("/api/history/{account_type}")
async def get_trade_history(account_type: str, current_user = Depends(get_current_user)):
    history = []
    async for position in db.positions.find({"user_id": current_user['user_id'], "account_type": account_type, "status": "closed"}).sort("closed_at", -1):
        position['_id'] = str(position['_id'])
        history.append(position)
    return history

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)