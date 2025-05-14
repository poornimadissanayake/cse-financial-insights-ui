# CSE Financial Insights

A comprehensive solution for analyzing quarterly financial reports from companies listed on the Colombo Stock Exchange (CSE).

## Project Overview

This project provides tools for:

- Scraping quarterly financial reports from CSE-listed companies
- Processing and structuring financial data
- Visualizing financial metrics through an interactive dashboard
- Querying financial data using natural language

## Companies Analyzed

- Dipped Products PLC (DIPD.N0000)
- Richard Pieris Exports PLC (REXP.N0000)

## Setup Instructions

### Prerequisites

- Python 3.11.9
- pip (Python package manager)
- Git
- Node.js 18+ (for frontend)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/cse-financial-insights-ui.git
cd cse-financial-insights
```

2. Backend Setup:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

3. Frontend Setup:

```bash
# Install frontend dependencies
cd frontend
npm install
```

### Environment Variables

1. Create a `.env` file in the root directory:

```bash
touch .env
```

2. Add the following environment variables:

```env
# OpenAI API Key for data extraction
OPENAI_API_KEY=your_openai_api_key_here
```

3. For the OpenAI API key:
   - Sign up for an account at [OpenAI Platform](https://platform.openai.com)
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key and paste it in your `.env` file

Note: Never commit the `.env` file to version control. It's already added to `.gitignore`.

### Running the Application

#### Backend Setup

1. Start the FastAPI backend:

```bash
cd backend
uvicorn app.main:app --reload
```

2. Run the data processing scripts:

```bash
# Run the scraper
python scripts/scraper/scraper.py

# Process the data
python scripts/processor/extract_from_pdfs.py
```

#### Frontend Setup

1. Launch the Next.js frontend:

```bash
cd frontend
npm run dev
```

2. Access the dashboard at `http://localhost:3000`

## Project Structure

```
cse-financial-insights/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routers/           # API endpoints
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── companies/
│   │   ├── components/
│   │   │   └── ui/
│   │   │       └── chat/      # Chatbot UI components
│   │   └── lib/
│   │       └── api.ts         # API calls
│   └── package.json
├── scripts/
│   ├── scraper/
│   │   └── scraper.py
│   └── processor/
│       ├── extract_from_pdfs.py
│       ├── openai_data_extractor.py
│       └── manual_data_extractor.py
├── data/
│   ├── raw/
│   └── processed/
│       └── jsons/             # Processed output
├── tests/                     # (optional) for unit/integration tests
└── README.md
```

## API Endpoints

1. `GET /api/companies`
   - Returns list of unique companies with their latest quarter data

2. `GET /api/companies/{symbol}/financials`
   - Returns quarterly financial data for a specific company
   - Query params: `?year=2024` (optional)

## Features

- Automated scraping of quarterly financial reports
- Data cleaning and standardization
- Interactive financial dashboard with Next.js
- RESTful API with FastAPI
- Historical trend analysis
- Comparative company analysis
- Modern, interactive charts built with [shadcn/ui charts](https://ui.shadcn.com/charts) and [Recharts](https://recharts.org/)
- Dark mode support for all visualizations

## Data Points Collected

- Revenue
- Cost of Goods Sold (COGS)
- Gross Profit
- Other Income
- Distribution Costs
- Administrative Expenses
- Operating Income
- Finance Costs
- Finance Income
- Share of Profit Equity Investee
- Profit Before Tax
- Tax Expense
- Net Income
- EPS (Basic)
- EPS (Diluted)
- Dividend per Share


## Data Processing

- OpenAI is used for extracting structured data from financial PDFs.
- All extracted data is post-processed for consistency and accuracy.



## Visualization

The dashboard uses [shadcn/ui charts](https://ui.shadcn.com/charts) (built on [Recharts](https://recharts.org/)) for all financial visualizations. Charts are interactive, responsive, and support both light and dark modes. Currency metrics are displayed in LKR millions (M) for clarity, and all axes/tooltips are clearly labeled. **Y-axis and tooltips for currency metrics in charts are always shown in LKR millions (M).** Table views use sticky columns (Quarter and Year) and right-aligned numbers for professional readability.

### Comparison Chart

A key feature of the dashboard is the **Company Comparison Chart**, which allows users to:
- Compare two companies financial metrics (e.g., Revenue, Net Income, Operating Income) over time.
- Choose a specific metric and a year range for focused analysis.
- Instantly visualize trends, differences, and performance between companies with color-coded lines/areas and a clear legend.
- Interact with tooltips to see exact values for each company at any point in time.

This comparison chart is implemented using shadcn/ui's AreaChart and related components, providing a modern, accessible, and visually appealing way to analyze financial data.

## Chatbot / Natural Language Querying

The dashboard includes a built-in chatbot that allows users to query financial data using natural language. This feature is powered by OpenAI's language models and is integrated into the frontend for a seamless user experience.

**How it works:**
- Users can ask questions about company financials (e.g., "What was the net income for DIPD in Q2 2023?" or "Compare the operating income of REXP and DIPD for the last 3 years.").
- The chatbot interprets the query, fetches the relevant data from the backend, and returns a human-readable answer.
- The backend uses OpenAI's API to process and understand user queries, leveraging both the extracted financial data and the model's reasoning capabilities.
- The chatbot can answer questions about trends, comparisons, and specific financial metrics, and can guide users to the relevant visualizations in the dashboard.

**Technologies used:**
- [OpenAI GPT API](https://platform.openai.com/docs/guides/gpt)
- FastAPI backend for query processing and data retrieval
- Next.js frontend for chat UI and integration

**Limitations:**
- It is currently focused on the two supported companies (DIPD, REXP) and the available financial metrics.


## Known Limitations / Future Work

- Only two companies (DIPD, REXP) are currently supported, but the system is extensible.
- Extraction accuracy depends on the quality of the PDF and the OpenAI model.
- Further enhancements could include more advanced natural language querying based on the past memories, additional companies financial metrics.

## 📃 License

This repository is created for evaluation purposes as part of a technical assessment.

---

**Note:** The frontend/README.md is the default Next.js template. For full setup and usage instructions, see this main README.

