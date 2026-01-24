from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()
postgres: list[dict]

@app.get('/aisql', response_model=dict)
def sql_query():
 pass