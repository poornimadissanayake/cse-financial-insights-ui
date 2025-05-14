const API_BASE_URL = 'http://localhost:8000/api';

export interface Company {
    symbol: string;
    latest_quarter: string;
    latest_year: string;
}

export interface FinancialMetrics {
    revenue: number | null;
    cost_of_goods_sold: number | null;
    gross_profit: number | null;
    other_income: number | null;
    distribution_costs: number | null;
    administrative_expenses: number | null;
    operating_income: number | null;
    finance_costs: number | null;
    finance_income: number | null;
    share_of_profit_equity_investee: number | null;
    profit_before_tax: number | null;
    tax_expense: number | null;
    net_income: number | null;
    eps_basic: number | null;
    eps_diluted: number | null;
    dividend_per_share: number | null;
}

export interface QuarterlyReport {
    quarter: string;
    year: string;
    financial_metrics: FinancialMetrics;
}

export async function getCompanies(): Promise<Company[]> {
    const response = await fetch(`${API_BASE_URL}/companies`);
    const data = await response.json();
    return data.companies;
}

export async function getCompanyFinancials(symbol: string, year?: string): Promise<QuarterlyReport[]> {
    const url = year
        ? `${API_BASE_URL}/companies/${symbol}/financials?year=${year}`
        : `${API_BASE_URL}/companies/${symbol}/financials`;
    const response = await fetch(url);
    return response.json();
} 