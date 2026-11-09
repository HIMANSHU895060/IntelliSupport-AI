from mcp.server.fastmcp import FastMCP
from app.rag import rag
from app.database import SessionLocal
from app.models import Ticket
import uuid
mcp=FastMCP("IntelliSupport MCP Server")
@mcp.tool()
def search_knowledge(query:str)->list[dict]:
    """Search the IntelliSupport knowledge base and return relevant source chunks."""
    return rag.search(query,4)
@mcp.tool()
def create_support_ticket(subject:str,description:str,customer_email:str,priority:str="medium")->dict:
    """Create a support ticket. This tool records a request; it does not approve refunds or account changes."""
    if priority not in {"low","medium","high","critical"}: raise ValueError("Invalid priority")
    tid="IS-"+uuid.uuid4().hex[:8].upper()
    with SessionLocal() as db:
        db.add(Ticket(id=tid,subject=subject[:190],description=description,category="mcp-created",priority=priority,status="open",customer_email=customer_email))
        db.commit()
    return {"ticket_id":tid,"status":"open"}
@mcp.tool()
def list_open_tickets()->list[dict]:
    """List open support tickets. Protect this MCP server; do not expose it to untrusted clients."""
    with SessionLocal() as db:
        rows=db.query(Ticket).filter(Ticket.status=="open").order_by(Ticket.created_at.desc()).limit(50).all()
        return [{"id":x.id,"subject":x.subject,"priority":x.priority,"customer_email":x.customer_email} for x in rows]
if __name__=="__main__": mcp.run(transport="stdio")
