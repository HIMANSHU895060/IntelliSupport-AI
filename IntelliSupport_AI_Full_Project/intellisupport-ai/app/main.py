from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import uuid, json, asyncio
from app.database import Base, engine, get_db, SessionLocal
from app.models import User, Ticket, Conversation
from app.schemas import RegisterIn, LoginIn, ChatIn, TicketIn, StatusIn, RoleIn
from app.security import hash_password, verify_password, create_token, current_user, require_roles
from app.config import settings
from app.agents import run_workflow
from app.rag import rag
app=FastAPI(title="IntelliSupport AI",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
Base.metadata.create_all(bind=engine)
@app.get("/")
def home(): return FileResponse("app/static/index.html")
@app.get("/api/health")
def health(): return {"status":"ok","orchestration":"LangGraph","rag":"hybrid lexical/optional semantic","mcp":"separate stdio server"}
@app.post("/api/auth/register")
def register(data:RegisterIn,db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=data.email).first(): raise HTTPException(409,"Email already registered")
    first=db.query(User).count()==0
    role="admin" if first and settings.allow_first_user_admin else "customer"
    u=User(name=data.name,email=data.email,password_hash=hash_password(data.password),role=role)
    db.add(u);db.commit();db.refresh(u)
    return {"access_token":create_token(u),"token_type":"bearer","user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}
@app.post("/api/auth/login")
def login(data:LoginIn,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=data.email).first()
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":create_token(u),"token_type":"bearer","user":{"id":u.id,"name":u.name,"email":u.email,"role":u.role}}
@app.get("/api/auth/me")
def me(u:User=Depends(current_user)): return {"id":u.id,"name":u.name,"email":u.email,"role":u.role}
@app.get("/api/knowledge/search")
def search_knowledge(q:str,k:int=4,u:User=Depends(current_user)): return rag.search(q,max(1,min(k,10)))
@app.get("/api/knowledge")
def knowledge(u:User=Depends(current_user)):
    return [{"id":d["id"],"title":d["title"],"text":d["text"]} for d in rag.records]
@app.post("/api/chat")
def chat(data:ChatIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    state=run_workflow(data.message,u.email)
    ticket_id=None
    if state.get("ticket_needed"):
        ticket_id="IS-"+uuid.uuid4().hex[:8].upper()
        db.add(Ticket(id=ticket_id,subject=data.message[:190],description=data.message,category=state["category"],priority=state["priority"],status="open",customer_email=u.email))
    db.add(Conversation(user_id=u.id,message=data.message,response=state["response"],category=state["category"]))
    db.commit()
    return {"response":state["response"],"category":state["category"],"priority":state["priority"],"sentiment":state["sentiment"],"ticket_id":ticket_id,"human_review_required":state.get("human_review",False),"sources":[{"id":x["source"],"title":x["title"],"score":x["score"]} for x in state.get("retrieved",[])],"events":state["events"]}
@app.get("/api/tickets")
def tickets(db:Session=Depends(get_db),u:User=Depends(current_user)):
    q=db.query(Ticket)
    if u.role=="customer": q=q.filter_by(customer_email=u.email)
    return [{"id":t.id,"subject":t.subject,"description":t.description,"category":t.category,"priority":t.priority,"status":t.status,"customer_email":t.customer_email,"assigned_to":t.assigned_to,"created_at":t.created_at.isoformat()} for t in q.order_by(Ticket.created_at.desc()).all()]
@app.post("/api/tickets")
def create_ticket(data:TicketIn,db:Session=Depends(get_db),u:User=Depends(current_user)):
    tid="IS-"+uuid.uuid4().hex[:8].upper()
    t=Ticket(id=tid,subject=data.subject,description=data.description,category=data.category,priority=data.priority,status="open",customer_email=u.email)
    db.add(t);db.commit()
    return {"id":tid,"status":"open"}
@app.patch("/api/tickets/{ticket_id}")
def update_ticket(ticket_id:str,data:StatusIn,db:Session=Depends(get_db),u:User=Depends(require_roles("support","admin"))):
    if data.status not in {"open","in_progress","resolved","closed"}: raise HTTPException(400,"Invalid status")
    t=db.get(Ticket,ticket_id)
    if not t: raise HTTPException(404,"Ticket not found")
    t.status=data.status;t.updated_at=datetime.now(timezone.utc);db.commit()
    return {"ok":True,"id":ticket_id,"status":t.status}
@app.get("/api/admin/overview")
def overview(db:Session=Depends(get_db),u:User=Depends(require_roles("admin","support"))):
    return {"users":db.query(User).count(),"tickets":db.query(Ticket).count(),"open":db.query(Ticket).filter_by(status="open").count(),"resolved":db.query(Ticket).filter_by(status="resolved").count(),"conversations":db.query(Conversation).count()}
@app.get("/api/admin/users")
def users(db:Session=Depends(get_db),u:User=Depends(require_roles("admin"))):
    return [{"id":x.id,"name":x.name,"email":x.email,"role":x.role} for x in db.query(User).all()]
@app.patch("/api/admin/users/{user_id}/role")
def set_role(user_id:int,data:RoleIn,db:Session=Depends(get_db),u:User=Depends(require_roles("admin"))):
    if data.role not in {"customer","support","admin"}: raise HTTPException(400,"Invalid role")
    target=db.get(User,user_id)
    if not target: raise HTTPException(404,"User not found")
    if target.id==u.id and data.role!="admin": raise HTTPException(400,"You cannot remove your own admin role")
    target.role=data.role;db.commit()
    return {"ok":True,"user_id":user_id,"role":data.role}
@app.websocket("/ws/chat")
async def ws_chat(ws:WebSocket):
    await ws.accept()
    try:
        token=ws.query_params.get("token","")
        import jwt
        payload=jwt.decode(token,settings.app_secret_key,algorithms=["HS256"])
        with SessionLocal() as db: user=db.get(User,int(payload["sub"]))
        if not user: await ws.close(code=4401);return
        await ws.send_json({"type":"connected","user":user.email})
        while True:
            msg=await ws.receive_text()
            try: data=json.loads(msg); prompt=data.get("message","")
            except Exception: prompt=msg
            state=run_workflow(prompt,user.email)
            for event in state["events"]:
                await ws.send_json({"type":"agent_event",**event})
                await asyncio.sleep(0.12)
            await ws.send_json({"type":"final","response":state["response"],"category":state["category"],"priority":state["priority"]})
    except WebSocketDisconnect: pass
    except Exception:
        await ws.close(code=4401)
app.mount("/static",StaticFiles(directory="app/static"),name="static")
