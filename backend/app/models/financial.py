from pydantic import BaseModel
from typing import Optional, List, Dict

class FinancialMetrics(BaseModel):
    revenue: Optional[float] = None
    cost_of_goods_sold: Optional[float] = None
    gross_profit: Optional[float] = None
    other_income: Optional[float] = None
    distribution_costs: Optional[float] = None
    administrative_expenses: Optional[float] = None
    operating_income: Optional[float] = None
    finance_costs: Optional[float] = None
    finance_income: Optional[float] = None
    share_of_profit_equity_investee: Optional[float] = None
    profit_before_tax: Optional[float] = None
    tax_expense: Optional[float] = None
    net_income: Optional[float] = None
    eps_basic: Optional[float] = None
    eps_diluted: Optional[float] = None
    dividend_per_share: Optional[float] = None

class QuarterlyReport(BaseModel):
    quarter: str
    year: str
    financial_metrics: FinancialMetrics

class Company(BaseModel):
    symbol: str
    latest_quarter: str
    latest_year: str

class CompanyList(BaseModel):
    companies: List[Company] 