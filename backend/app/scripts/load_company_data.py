import os
import json
from pathlib import Path
from app.services.document_service import document_service

def load_company_data():
    # Define paths
    processed_dir = Path("../../data/processed/jsons")  # Updated path
    
    # Process each company's JSON data
    json_files = list(processed_dir.glob("*.json"))
    
    for json_file in json_files:
        company_name = json_file.stem.split('_')[0]  # Get company name from filename (e.g., DIPD from DIPD_2024_03_31.json)
        print(f"Processing data for {company_name} from {json_file.name}...")
        
        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            print(f"Successfully loaded {json_file.name}")
            
            # Process the JSON data
            document_service.process_json_data(json_data, company_name)
            print(f"Successfully processed {json_file.name}")
            
        except Exception as e:
            print(f"Error processing {json_file.name}: {str(e)}")
    
    print("Data loading complete!")

if __name__ == "__main__":
    load_company_data() 