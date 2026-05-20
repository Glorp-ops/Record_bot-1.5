import datetime

from pydantic import BaseModel


class Lesson_(BaseModel):
    name: str

class User_(BaseModel):
    tg_id: int
    name: str
    role: str

class Record_(BaseModel):
    date: datetime.date
    time: datetime.time
    tg_id: int
    lesson: str