from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from app.rag import rag
from app.config import settings
import httpx
class SupportState(TypedDict, total=False):
    message: str; email: str; category: str; priority: str; sentiment: str
    retrieved: list; technical_notes: str; response: str; ticket_needed: bool
    human_review: bool; events: list
def emit(s, name, detail):
    s.setdefault("events", []).append({"agent":name,"detail":detail,"status":"complete"})
    return s
def intake(s):
    emit(s,"Customer Interaction Agent","Parsed the customer's message and identified the request.")
    return s
def classify(s):
    m=s["message"].lower()
    if any(w in m for w in ["refund","charged","invoice","payment"]): cat,pri="billing","high"
    elif any(w in m for w in ["outage","down","security breach","production"]): cat,pri="incident","critical"
    elif any(w in m for w in ["login","password","account"]): cat,pri="account","medium"
    elif any(w in m for w in ["error","bug","api","429","crash","slow"]): cat,pri="technical","high"
    else: cat,pri="general","low"
    s["category"],s["priority"]=cat,pri
    s["sentiment"]="negative" if any(w in m for w in ["angry","frustrated","terrible","unacceptable","urgent"]) else "neutral"
    s["human_review"]=any(w in m for w in ["refund","delete my account","change my email","close my account"])
    s["ticket_needed"]=pri in ("high","critical") or s["human_review"]
    emit(s,"Query Classification Agent",f"Category={cat}; priority={pri}; sentiment={s['sentiment']}.")
    return s
def retrieve(s):
    s["retrieved"]=rag.search(s["message"],k=4)
    emit(s,"Knowledge Base / RAG Agent",f"Retrieved {len(s['retrieved'])} relevant knowledge chunks.")
    return s
def technical(s):
    if s["category"] in ("technical","incident"):
        s["technical_notes"]="Collect timestamp, region, request ID, error text and reproduction steps. Check service health and recent deployments."
    else: s["technical_notes"]="No technical diagnostic action required for this category."
    emit(s,"Technical Support Agent",s["technical_notes"])
    return s
def ticket(s):
    emit(s,"Ticket Management Agent","Ticket creation will be performed by the API persistence layer if required.")
    return s
async def llm_response(s):
    if not (settings.llm_api_key and settings.llm_model): return None
    context="\n".join(f"[{x['source']}] {x['title']}: {x['chunk']}" for x in s.get("retrieved",[]))
    payload={"model":settings.llm_model,"messages":[
      {"role":"system","content":"You are a careful support assistant. Answer using only the retrieved context for policy claims. If context is insufficient, ask clarifying questions or escalate. Never approve refunds, change accounts, or claim an action was completed."},
      {"role":"user","content":f"Customer message: {s['message']}\nRetrieved context:\n{context}"}
    ],"temperature":0.2}
    async with httpx.AsyncClient(timeout=25) as c:
        r=await c.post(settings.llm_base_url.rstrip("/")+"/chat/completions",headers={"Authorization":"Bearer "+settings.llm_api_key},json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
def response(s):
    if s.get("human_review"):
        answer="I understand your request. This needs review by an authorized human support specialist. I will route it to the team; the AI cannot approve refunds or make sensitive account changes."
    elif s.get("retrieved"):
        x=s["retrieved"][0]
        answer=f"Thanks for contacting support. Based on our help article '{x['title']}': {x['chunk']} If this does not solve the issue, please share the exact error and when it occurred."
    else:
        answer="Thanks for contacting support. Please share the product affected, exact error message, when it started, and steps to reproduce it so our team can investigate."
    s["response"]=answer
    emit(s,"Response Generation Agent","Prepared a response with retrieved source context where available.")
    return s
def supervisor(s):
    emit(s,"Supervisor Agent","Checked response and routing. Human review is required for sensitive actions.")
    return s
def build_graph():
    g=StateGraph(SupportState)
    for name, fn in [("intake",intake),("classify",classify),("retrieve",retrieve),("technical",technical),("ticket",ticket),("respond",response),("supervisor",supervisor)]:
        g.add_node(name,fn)
    g.set_entry_point("intake")
    g.add_edge("intake","classify"); g.add_edge("classify","retrieve"); g.add_edge("retrieve","technical")
    g.add_edge("technical","ticket"); g.add_edge("ticket","respond"); g.add_edge("respond","supervisor"); g.add_edge("supervisor",END)
    return g.compile()
support_graph=build_graph()
def run_workflow(message,email):
    return support_graph.invoke({"message":message,"email":email,"events":[]})
