#!/usr/bin/env python3
"""
FedLab Search API - быстрый поиск мероприятий
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from simple_search import SimpleSearch

app = FastAPI(title="FedLab Search", version="1.0")
searcher = SimpleSearch()
searcher.load_events('/root/LabDoctorM/projects/fedlab_parser/fedlab_events.json')

class SearchQuery(BaseModel):
    query: str
    limit: int = 10

class SearchResult(BaseModel):
    score: float
    title: str
    location: str
    month: str

@app.post("/search", response_model=list[SearchResult])
def search_items(q: SearchQuery):
    return searcher.search(q.query, q.limit)

@app.get("/events")
def list_events():
    return searcher.documents

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9999)