import os

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/settings", tags=["Settings"])


class ProviderChange(BaseModel):
    provider: str = Field(pattern="^(local|gemini|ollama|openai)$")


@router.post("/provider")
def change_provider(payload: ProviderChange):
    os.environ["LLM_PROVIDER"] = payload.provider
    return {"provider": payload.provider, "message": f"Evaluation provider changed to {payload.provider}."}


@router.get("/provider")
def current_provider():
    return {"provider": os.getenv("LLM_PROVIDER", "local")}
