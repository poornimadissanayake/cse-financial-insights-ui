from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..models.financial import Company, QuarterlyReport, CompanyList
from ..services.data_service import DataService

router = APIRouter()
data_service = DataService()

@router.get("/companies", response_model=CompanyList)
async def get_companies():
    """Get list of all companies with their latest quarter data"""
    companies = data_service.get_companies()
    return CompanyList(companies=companies)

@router.get("/companies/{symbol}/financials", response_model=List[QuarterlyReport])
async def get_company_financials(symbol: str, year: Optional[str] = None):
    """Get quarterly financial data for a specific company"""
    files = data_service._get_company_files(symbol)
    if not files:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    reports = data_service.get_company_financials(symbol, year)
    return reports 