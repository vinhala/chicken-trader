from pydantic import BaseModel


class BrokerSettingIn(BaseModel):
    broker_name: str
    preferred_exchanges: str = ""


class BrokerSettingOut(BaseModel):
    broker_name: str
    preferred_exchanges: str
