from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.entities import User, UserBrokerSetting
from app.schemas.broker import BrokerSettingIn, BrokerSettingOut


router = APIRouter(prefix="/broker", tags=["broker"])


@router.get("/settings", response_model=BrokerSettingOut)
def get_setting(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BrokerSettingOut:
    row = db.query(UserBrokerSetting).filter(UserBrokerSetting.user_id == current_user.id).first()
    if not row:
        row = UserBrokerSetting(user_id=current_user.id, broker_name="Default", preferred_exchanges="")
        db.add(row)
        db.commit()
        db.refresh(row)
    return BrokerSettingOut(broker_name=row.broker_name, preferred_exchanges=row.preferred_exchanges)


@router.put("/settings", response_model=BrokerSettingOut)
def put_setting(payload: BrokerSettingIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BrokerSettingOut:
    row = db.query(UserBrokerSetting).filter(UserBrokerSetting.user_id == current_user.id).first()
    if not row:
        row = UserBrokerSetting(user_id=current_user.id, broker_name=payload.broker_name, preferred_exchanges=payload.preferred_exchanges)
        db.add(row)
    else:
        row.broker_name = payload.broker_name
        row.preferred_exchanges = payload.preferred_exchanges
    db.commit()
    db.refresh(row)
    return BrokerSettingOut(broker_name=row.broker_name, preferred_exchanges=row.preferred_exchanges)
