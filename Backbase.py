from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

class SqlAI(BaseModel):
    username: str
    password: str

class SqlSystem(SqlAI):
    table_name: str
    column: int