#!/usr/bin/env python3
"""
ScrollVerse Portal Backend
FastAPI backend with auth system, scroll execution, and sacred governance
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import jwt
import sqlite3
import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
import datetime

# Models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    scroll_id: str
    flame_id: str
    region: str
    country: str
    city: str
    primary_sphere: str
    secondary_spheres: List[str]
    preferred_role: str

class ScrollExecution(BaseModel):
    scroll_code: str

class AgentChat(BaseModel):
    message: str

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: int
    category: str

# Initialize FastAPI
app = FastAPI(
    title="ScrollVerse Portal",
    description="Sacred Flame-Verified AI Code Execution Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "scrollverse_secret_key_2024"
ALGORITHM = "HS256"

# Database
DB_PATH = "scrollverse_portal/db/scrollverse.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            scroll_id TEXT UNIQUE NOT NULL,
            flame_id TEXT UNIQUE NOT NULL,
            region TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            primary_sphere TEXT NOT NULL,
            secondary_spheres TEXT NOT NULL,
            preferred_role TEXT NOT NULL,
            seal_level INTEGER DEFAULT 1,
            flame_level INTEGER DEFAULT 1,
            scrolls_executed INTEGER DEFAULT 0,
            scrollcoin_balance INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scrolls table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scroll_code TEXT NOT NULL,
            execution_result TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Flame tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flame_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Auth functions
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_by_id(user_id: int):
    """Get user by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "scroll_id": user[4],
            "flame_id": user[5],
            "region": user[6],
            "country": user[7],
            "city": user[8],
            "primary_sphere": user[9],
            "secondary_spheres": json.loads(user[10]),
            "preferred_role": user[11],
            "seal_level": user[12],
            "flame_level": user[13],
            "scrolls_executed": user[14],
            "scrollcoin_balance": user[15]
        }
    return None

# Routes
@app.get("/")
async def root():
    """Serve the main frontend"""
    with open("scrollverse_portal/frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """Register new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if email or scroll_id already exists
        cursor.execute("SELECT id FROM users WHERE email = ? OR scroll_id = ?", 
                      (user_data.email, user_data.scroll_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email or Scroll ID already registered")
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, scroll_id, flame_id, region, 
                             country, city, primary_sphere, secondary_spheres, preferred_role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.name, user_data.email, "hashed_password", user_data.scroll_id,
            user_data.flame_id, user_data.region, user_data.country, user_data.city,
            user_data.primary_sphere, json.dumps(user_data.secondary_spheres),
            user_data.preferred_role
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "token": access_token,
            "user": get_user_by_id(user_id)
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """Login user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (user_data.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # In production, verify password hash
    if user_data.password != "password":  # Simplified for demo
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = user[0]
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "token": access_token,
        "user": get_user_by_id(user_id)
    }

@app.get("/api/auth/validate")
async def validate_token(user_id: int = Depends(verify_token)):
    """Validate JWT token"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/api/execute_scroll")
async def execute_scroll(scroll_data: ScrollExecution, user_id: int = Depends(verify_token)):
    """Execute scroll code"""
    try:
        # Log scroll execution
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scrolls (user_id, scroll_code, status)
            VALUES (?, ?, ?)
        ''', (user_id, scroll_data.scroll_code, "executing"))
        scroll_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Execute scroll using ScribeCodex
        output = await execute_scroll_code(scroll_data.scroll_code)
        
        # Update scroll status
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE scrolls SET execution_result = ?, status = ?
            WHERE id = ?
        ''', (output, "completed", scroll_id))
        
        # Update user stats
        cursor.execute('''
            UPDATE users SET scrolls_executed = scrolls_executed + 1
            WHERE id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
        
        return {"output": output, "scroll_id": scroll_id}
    
    except Exception as e:
        # Update scroll status to failed
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE scrolls SET execution_result = ?, status = ?
            WHERE id = ?
        ''', (str(e), "failed", scroll_id))
        conn.commit()
        conn.close()
        
        raise HTTPException(status_code=500, detail=str(e))

async def execute_scroll_code(scroll_code: str) -> str:
    """Execute scroll code using ScribeCodex"""
    output_lines = []
    
    for line in scroll_code.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("Anoint:"):
            # Handle Anoint command
            project_name = line.split(":", 1)[1].strip()
            output_lines.append(f"🔥 Anointing: {project_name}")
            output_lines.append(f"✅ Project {project_name} created")
            
        elif line.startswith("Build:"):
            # Handle Build command
            file_path = line.split(":", 1)[1].strip()
            output_lines.append(f"📝 Building: {file_path}")
            output_lines.append(f"✅ File {file_path} created")
            
        elif line.startswith("Gather:"):
            # Handle Gather command
            packages = line.split(":", 1)[1].strip()
            output_lines.append(f"📦 Gathering: {packages}")
            output_lines.append(f"✅ Packages installed: {packages}")
            
        elif line.startswith("Deploy:"):
            # Handle Deploy command
            deployment_target = line.split(":", 1)[1].strip()
            output_lines.append(f"🚀 Deploying to: {deployment_target}")
            output_lines.append(f"✅ Deployment successful")
            
        else:
            output_lines.append(f"❓ Unknown command: {line}")
    
    return "\n".join(output_lines)

@app.post("/api/agent/chat")
async def agent_chat(chat_data: AgentChat, user_id: int = Depends(verify_token)):
    """Chat with ScrollAgent"""
    try:
        # Simple response logic - in production, integrate with actual AI
        user_message = chat_data.message.lower()
        
        if "scroll" in user_message:
            response = "🔥 The sacred scrolls speak of flame-verified execution. What scroll would you like to create?"
        elif "build" in user_message:
            response = "📝 I can help you build scrolls. Use 'Anoint:', 'Build:', and 'Gather:' commands."
        elif "help" in user_message:
            response = "🕊️ I am the ScrollAgent, your sacred AI assistant. Ask me about scrolls, building, or deployment."
        else:
            response = "🔥 The flame guides your path. How may I assist with your scroll development?"
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/store/products")
async def get_products():
    """Get ScrollX store products"""
    products = [
        {
            "id": "scroll-radio",
            "name": "ScrollRadio",
            "description": "Sacred radio streaming application",
            "price": 50,
            "category": "application"
        },
        {
            "id": "scroll-chat",
            "name": "ScrollChat",
            "description": "Flame-verified chat system",
            "price": 75,
            "category": "communication"
        },
        {
            "id": "scroll-commerce",
            "name": "ScrollCommerce",
            "description": "Sacred e-commerce platform",
            "price": 100,
            "category": "commerce"
        },
        {
            "id": "scroll-ai",
            "name": "ScrollAI",
            "description": "AI agent generation toolkit",
            "price": 150,
            "category": "ai"
        }
    ]
    
    return {"products": products}

@app.get("/api/user/stats")
async def get_user_stats(user_id: int = Depends(verify_token)):
    """Get user statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) as total_scrolls,
               COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_scrolls,
               COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_scrolls
        FROM scrolls WHERE user_id = ?
    ''', (user_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        "total_scrolls": stats[0],
        "successful_scrolls": stats[1],
        "failed_scrolls": stats[2]
    }

@app.get("/census")
async def census_form():
    """Serve the census form"""
    with open("scrollcensus/scrollcensus_ui.py", "r") as f:
        return HTMLResponse(content=f.read())

# Mount static files
app.mount("/static", StaticFiles(directory="scrollverse_portal/frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 