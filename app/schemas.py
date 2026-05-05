from pydantic import BaseModel

class Patient(BaseModel):
    age: int
    larynx: int
    parotide: int
    ethmoide: int