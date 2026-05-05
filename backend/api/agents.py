"""
Agent endpoints: /agents/discovery, /agents/filter, /agents/outreach.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.agent import (
    AgentResponse,
    DiscoveryRequest,
    FilterRequest,
    OutreachDraft,
    OutreachRequest,
)

router = APIRouter(prefix="/agents", tags=["agents"])

# Lazy singletons — built on first use so module imports never trigger
# Pinecone/LLM boot. Keeps CI, tests, and cold-start debugging fast.
_singletons: dict[str, object] = {}


def _discovery():
    if "discovery" not in _singletons:
        from backend.agents.discovery_agent import DiscoveryAgent
        _singletons["discovery"] = DiscoveryAgent()
    return _singletons["discovery"]


def _filtering():
    if "filtering" not in _singletons:
        from backend.agents.filtering_agent import FilteringAgent
        _singletons["filtering"] = FilteringAgent()
    return _singletons["filtering"]


def _outreach():
    if "outreach" not in _singletons:
        from backend.agents.outreach_agent import OutreachAgent
        _singletons["outreach"] = OutreachAgent()
    return _singletons["outreach"]


@router.post("/discovery", response_model=AgentResponse)
def run_discovery(req: DiscoveryRequest, db: Session = Depends(get_db)):
    try:
        return _discovery().run(db, req)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery agent error: {e}")


@router.post("/filter", response_model=AgentResponse)
def run_filter(req: FilterRequest, db: Session = Depends(get_db)):
    try:
        return _filtering().run(db, req)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter agent error: {e}")


@router.post("/outreach", response_model=OutreachDraft)
def run_outreach(req: OutreachRequest, db: Session = Depends(get_db)):
    try:
        return _outreach().draft(db, req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outreach agent error: {e}")
