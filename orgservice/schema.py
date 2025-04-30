from ninja import Schema
from typing import Optional

class GoodStandingSchema(Schema):
    name: str
    idNumber: Optional[str] = None
    status: Optional[str] = None
    form: Optional[str] = None
    formationDate: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None

