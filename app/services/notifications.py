import requests
from exponent_server_sdk import PushClient, PushMessage, DeviceNotRegisteredError
from sqlalchemy.orm import Session
from app.models.notifications import PushToken
from app.config import settings

# sesión autenticada con tu token
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {settings.EXPO_ACCESS_TOKEN}",
    "Content-Type": "application/json",
})

def register_token(token: str, db: Session):
    existing = db.query(PushToken).filter_by(token=token).first()
    if not existing:
        db.add(PushToken(token=token))
        db.commit()

def broadcast(title: str, body: str, db: Session, data: dict = None):
    tokens = db.query(PushToken).all()
    print(tokens)
    if not tokens:
        return {"sent": 0}

    messages = [
        PushMessage(to=t.token, title=title, body=body, data=data, sound="default")
        for t in tokens
    ]

    responses = PushClient(session=session).publish_multiple(messages)

    # Limpiar tokens inválidos
    invalid = 0
    for token, response in zip(tokens, responses):
        try:
            response.validate_response()
        except DeviceNotRegisteredError:
            db.delete(token)
            invalid += 1

    db.commit()
    return {"sent": len(tokens) - invalid, "removed": invalid}