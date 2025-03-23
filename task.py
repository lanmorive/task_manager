import pydantic

class Task(pydantic.BaseModel):
    """
    Модель задачи
    """
    id_: int
    task: str
    priority: str
    date: str
    status: str
    
