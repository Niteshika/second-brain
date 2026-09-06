from typing import Optional
from pydantic import BaseModel

class ClusterResult(BaseModel):
    name: str
    chunk_count: int
    sources: list[str]

class BlindSpot(BaseModel):
    topic: str
    description: str


class Contradiction(BaseModel):
    note_1: str
    note_2: str
    reason: str
    source_1: str
    source_2: str


class StaleNote(BaseModel):
    title: str
    url: str
    last_edited: str
    age_days: int
    preview: str


class KnowledgeGapResult(BaseModel):
    clusters: list[ClusterResult]
    blind_spots: list[BlindSpot]
    contradictions: list[Contradiction]
    stale_notes: list[StaleNote]


class JobStartResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    status: str  # "running" | "done" | "error"
    result: Optional[KnowledgeGapResult] = None
    error: Optional[str] = None
