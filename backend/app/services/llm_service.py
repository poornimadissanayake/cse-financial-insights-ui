import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import logging
import httpx
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize LangChain components
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="output",
    max_token_limit=2000,  # Limit total tokens in memory
    k=10,  # Keep only the last 10 messages
)


class CompanyDataTool:
    def __init__(self):
        self.base_url = (
            "http://localhost:8000/api"  # FastAPI server URL with /api prefix
        )

    async def get_company_data(
        self, symbol: str, year: Optional[str] = None
    ) -> List[Dict]:
        """Fetch company financial data from the API"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/companies/{symbol}/financials"
                if year:
                    url += f"?year={year}"
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching company data: {str(e)}")
            return []


# Initialize the company data tool
company_tool = CompanyDataTool()

# Define the tools
tools = [
    StructuredTool.from_function(
        func=company_tool.get_company_data,
        name="get_company_financials",
        description="""Use this tool to get financial data for a specific company.
        Input should be a JSON string with 'symbol' (DIPD or REXP) and optional 'year'.
        Example: {"symbol": "DIPD", "year": "2023"}""",
        coroutine=company_tool.get_company_data,
    )
]

# Define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a friendly and knowledgeable CSE financial insights assistant specializing in DIPPED PRODUCTS PLC (DIPD) and Richard Pieris Exports PLC (REXP).
    Your role is to provide clear, concise financial analysis and insights while maintaining a conversational and helpful tone.
    
    When users greet you or engage in casual conversation:
    - Respond warmly and professionally
    - Briefly introduce yourself as a financial assistant for DIPD and REXP
    - Be ready to answer their financial questions directly or guide them if their query is unclear.
    
    For financial questions, focus on:
    - DIPPED PRODUCTS PLC (DIPD)
    - Richard Pieris Exports PLC (REXP)
    - Their financial performance
    - Their quarterly results
    - Comparisons between these two companies
    
    If asked about other companies or non-financial topics:
    - Acknowledge their question politely
    - Explain that you specialize in DIPD and REXP financial data
    - Offer to help with financial analysis of these companies
    
    Guidelines for answering questions:
    - **If the user's query directly asks for or strongly implies a request for investment advice (e.g., "what is the good company to invest?", "should I invest in DIPD or REXP?", "which company is better for investment?"), IMMEDIATELY proceed to the investment advice protocol outlined further below (fetch data for BOTH companies, compare, interpret with disclaimer). Do not default to a general greeting or ask for clarification if the investment intent seems clear.**
    - For specific metrics (profit, revenue, etc.), use the get_company_financials tool to fetch the data
    - Always provide the actual numbers when available
    - All financial values are in Sri Lankan Rupees (LKR)
    - Format numbers with commas for readability
    - If comparing companies, highlight key differences
    - If information is not available, clearly state that
    - For questions about specific quarters, fetch the relevant data using the tool
    - When asked for investment advice (e.g., 'which company is better to invest in?', 'should I invest in DIPD or REXP?', 'what\\'s a good investment?'), first use the `get_company_financials` tool to fetch recent data for BOTH DIPD and REXP. Then, provide a comparative analysis based *solely* on this fetched financial data. Based on this analysis, you can offer an interpretation of which company *appears* to exhibit more favorable trends or stronger key performance indicators from an investment perspective, clearly stating this is based on past data. Always conclude with a strong disclaimer: 'Please remember, this is not professional financial advice. These observations are based on past financial data and do not guarantee future performance. You should consult with a qualified financial advisor before making any investment decisions.' Avoid definitive predictions or speculative statements not directly and clearly supported by the comparative financial data.
    
    Available companies: DIPD, REXP
    Available quarters: Q1-Q4 (2023-2024)""",
        ),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}"),
    ]
)

# Create the agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
    memory=memory,
)


async def get_llm_response(message: str) -> str:
    """
    Get a response from the LLM model based on the user's message.
    Focus on CSE financial insights for DIPD and REXP.
    """
    try:
        logger.info(f"Processing message: {message}")
        response = await agent_executor.ainvoke({"input": message})
        logger.info(f"Agent response: {response}")
        return response["output"]
    except Exception as e:
        logger.error(f"Error in get_llm_response: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        return "I encountered an error while processing your request. Please try again."
