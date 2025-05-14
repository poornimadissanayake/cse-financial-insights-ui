import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from ..models.financial import Company, QuarterlyReport

class DataService:
    def __init__(self):
        # Get the absolute path to the data directory
        base_dir = Path(__file__).parent.parent.parent.parent
        self.data_dir = base_dir / "data" / "processed" / "jsons"
        
    def _get_all_files(self) -> List[Path]:
        return list(self.data_dir.glob("*.json"))
    
    def _get_company_files(self, symbol: str) -> List[Path]:
        return list(self.data_dir.glob(f"{symbol}_*.json"))
    
    def _read_json_file(self, file_path: Path) -> Dict:
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def get_companies(self) -> List[Company]:
        files = self._get_all_files()
        companies = {}
        
        for file in files:
            symbol = file.stem.split('_')[0]
            data = self._read_json_file(file)
            
            if symbol not in companies or (
                data['year'] > companies[symbol]['latest_year'] or
                (data['year'] == companies[symbol]['latest_year'] and
                 data['quarter'] > companies[symbol]['latest_quarter'])
            ):
                companies[symbol] = {
                    'latest_quarter': data['quarter'],
                    'latest_year': data['year']
                }
        
        return [
            Company(symbol=symbol, **data)
            for symbol, data in companies.items()
        ]
    
    def get_company_financials(self, symbol: str, year: Optional[str] = None) -> List[QuarterlyReport]:
        files = self._get_company_files(symbol)
        reports = []
        
        for file in files:
            data = self._read_json_file(file)
            if year is None or data['year'] == year:
                # Calculate operating_income if possible
                fm = data.get('financial_metrics', {})
                gross_profit = fm.get('gross_profit')
                other_income = fm.get('other_income', 0)
                distribution_costs = fm.get('distribution_costs')
                administrative_expenses = fm.get('administrative_expenses')
                # Only calculate if required fields are present
                if gross_profit is not None and distribution_costs is not None and administrative_expenses is not None:
                    calculated_oi = gross_profit + (other_income or 0) - abs(distribution_costs) - abs(administrative_expenses)
                    fm['operating_income'] = calculated_oi
                    data['financial_metrics'] = fm
                reports.append(QuarterlyReport(**data))
        
        return sorted(reports, key=lambda x: (x.year, x.quarter)) 