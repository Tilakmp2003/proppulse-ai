from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class DealStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"

class PropertyType(str, Enum):
    MULTIFAMILY = "Multifamily"
    OFFICE = "Office"
    RETAIL = "Retail"
    INDUSTRIAL = "Industrial"

class InvestmentCriteria(BaseModel):
    min_cash_on_cash: Optional[float] = 8.0
    min_cap_rate: Optional[float] = 6.0
    min_irr: Optional[float] = 12.0
    min_dscr: Optional[float] = 1.2
    max_year_built: Optional[int] = 1980
    max_price: Optional[float] = 5000000
    min_units: Optional[int] = 20
    max_units: Optional[int] = 100
    preferred_markets: Optional[List[str]] = []
    risk_tolerance: Optional[str] = "medium"

class DealCreate(BaseModel):
    upload_id: str
    investment_criteria: Optional[InvestmentCriteria] = None

class DealMetrics(BaseModel):
    cap_rate: float
    cash_on_cash: float
    irr: float
    net_present_value: float
    debt_service_coverage: float

class PropertyDetails(BaseModel):
    year_built: int
    square_footage: float
    units: int
    property_type: str
    market_value: float

class FinancialSummary(BaseModel):
    gross_rental_income: float
    operating_expenses: float
    net_operating_income: float
    cash_flow: float

class MarketData(BaseModel):
    comp_properties: List[Dict[str, Any]]
    neighborhood_score: float
    market_trends: str

class DealAnalysisResult(BaseModel):
    pass_fail: DealStatus
    score: float
    metrics: DealMetrics
    property_details: PropertyDetails
    financial_summary: FinancialSummary
    market_data: MarketData
    ai_analysis: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    id: str
    property_address: str
    analysis_result: DealAnalysisResult
    created_at: datetime

class Deal(BaseModel):
    id: str
    property_address: str
    property_type: PropertyType
    deal_size: float
    status: str
    created_at: datetime
    updated_at: datetime

class DealAnalysis(Deal):
    analysis_result: Optional[DealAnalysisResult] = None
