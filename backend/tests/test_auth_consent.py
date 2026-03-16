import pytest
from fastapi import HTTPException

from app.api.auth import register
from app.models.entities import DisclaimerConsent, User
from app.schemas.auth import RegisterRequest


def test_register_requires_disclaimer(db_session):
    payload = RegisterRequest(email="user1@example.com", password="password123", disclaimer_accepted=False)
    with pytest.raises(HTTPException):
        register(payload, db_session)


def test_register_stores_disclaimer_consent(db_session):
    payload = RegisterRequest(email="user2@example.com", password="password123", disclaimer_accepted=True)
    user = register(payload, db_session)

    stored_user = db_session.query(User).filter(User.email == user.email).first()
    consent = db_session.query(DisclaimerConsent).filter(DisclaimerConsent.user_id == stored_user.id).first()

    assert stored_user is not None
    assert consent is not None
    assert consent.disclaimer_text
