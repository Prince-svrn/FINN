from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from backend.domain import DEFAULT_CATEGORIES

Category=Literal['results','M&A','fund_raise','management_change','litigation','insider_trading','earnings_call','investor_meetings','credit_rating','dividend','bonus_split','capex','press_release','postal_ballot','agm_egm','pledging','unclassified']

class Citation(BaseModel):
    document_id:str
    page:int=Field(ge=1)
    quote:str=Field(min_length=8,max_length=1200)

class Fact(BaseModel):
    claim:str=Field(max_length=300)
    citation:Citation

class NumericGuidance(BaseModel):
    quarter_label:str
    metric:str
    promised_guidance_quote:str
    low:float|None=None
    high:float|None=None
    actual:float|None=None
    unit:str
    direction:Literal['higher','lower']='higher'
    period_match:bool=False
    basis_match:bool=False
    promise:Citation
    outcome:Citation|None=None

class Synthesis(BaseModel):
    business:list[Fact]=Field(default_factory=list,max_length=5)
    audit:list[NumericGuidance]=Field(default_factory=list,max_length=12)
    guidance:list[Fact]=Field(default_factory=list,max_length=8)
    bull:list[Fact]=Field(default_factory=list,max_length=3)
    bear:list[Fact]=Field(default_factory=list,max_length=3)
    governance:list[Fact]=Field(default_factory=list,max_length=8)

class FilingAnalysisSchema(BaseModel):
    category:Category
    materiality_score:int=Field(ge=0,le=100)
    headline:str=Field(max_length=300)
    # Model-extracted numeric cells require separate deterministic validation.
    results:list[dict]=Field(default_factory=list)

class Settings(BaseModel):
    price_threshold_pct:float=Field(default=3,ge=1,le=10)
    volume_multiplier_threshold:float=Field(default=2,ge=1.5,le=5)
    categories:list[Category]=Field(default_factory=lambda:DEFAULT_CATEGORIES.copy())

class ResearchRequest(BaseModel):
    symbol:str=Field(min_length=1,max_length=40)
    use_models:bool=False
    refresh:bool=False

class Pin(BaseModel):
    id:str=Field(min_length=1,max_length=150)
    symbol:str=Field(max_length=40)
    title:str=Field(max_length=500)
    note:str=Field(default='',max_length=2000)
    source_url:str=Field(default='',max_length=2000)
    source_label:str=Field(default='',max_length=300)
