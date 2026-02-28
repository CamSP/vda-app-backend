from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.notifications import RegisterTokenRequest, BroadcastRequest
from app.services.notifications import register_token, broadcast
from app.auth.api_key import verify_api_key

router = APIRouter()

# Lo llama la app al iniciarse (sin login)
@router.post("/register-token")
def register(req: RegisterTokenRequest, db: Session = Depends(get_db)):
    register_token(req.token, db)
    return {"ok": True}

# Lo llamas tú cuando quieres mandar un anuncio
@router.post("/broadcast", dependencies=[Depends(verify_api_key)])
def send_broadcast(req: BroadcastRequest, db: Session = Depends(get_db)):
    result = broadcast(req.title, req.body, db, req.data)
    return result