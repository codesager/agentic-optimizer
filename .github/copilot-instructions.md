# AI Coding Assistant Instructions for POMS

## Project Overview
POMS is a Multi-Agent SMA (Separately Managed Account) Customization Engine built with LangGraph. It orchestrates specialized agents to customize investment portfolios based on natural language mandates, using market data from Financial Modeling Prep API and CVXPY for optimization.

## Architecture & Key Components

### Core Workflow (LangGraph StateGraph in `src/graph.py`)
- **Mandate Agent** (`src/agents/mandate_agent.py`): Parses natural language into structured constraints using Pydantic models
- **Finviz Screener Agent** (`src/agents/finviz_screener_agent.py`): Screens stocks using finviz library based on criteria (market cap > large, EPS > 0) and applies sector filtering
- **Pricing Agent** (`src/agents/pricing_agent.py`): Retrieves historical prices using yfinance for screened stocks
- **Risk Model** (`src/graph.py::risk_model_node`): Calculates expected returns (mu) and covariance matrix (Sigma) from price data
- **Optimizer Agent** (`src/agents/optimizer_agent.py`): Generates CVXPY optimization code using GPT-4o-mini
- **Code Executor** (`src/graph.py::code_executor_node`): Safely executes generated code in isolated namespace
- **Reviewer Agent** (`src/graph.py::reviewer_agent_node`): Validates final portfolio against original constraints

### State Management (`src/state.py`)
Uses TypedDict-based `SMAState` for inter-agent communication:
- `user_mandate`: Raw natural language input
- `structured_constraints`: Parsed JSON constraints (excluded_sectors, max_position_weight, etc.)
- `screener_criteria`: Screening criteria for stock selection (market_cap_min, eps_max, etc.)
- `universe`: List of ticker symbols from screener
- `market_data`: Pandas DataFrame of historical prices from yfinance
- `risk_model`: Dict with numpy arrays `mu` and `Sigma`
- `generated_python_code`: CVXPY optimization code string
- `final_portfolio`: Dict mapping tickers to weights
- `feedback`: Error messages or reviewer comments

### Tools & Utilities
- **Finviz Library**: Used by screener agent for stock screening based on financial metrics
- **YFinance Library**: Used by pricing agent for downloading historical stock prices
- **Safe Executor** (`src/tools/executor.py`): Isolated code execution with pre-injected dependencies (numpy, cvxpy, mu, Sigma)
- **Risk Model** (`src/tools/risk_model.py`): Portfolio risk calculations (currently minimal)

## Development Workflow

### Setup & Environment
```bash
# Windows
setup_env.bat
# Linux/Mac
./setup_env.sh

# Or manually:
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix
pip install -r requirements.txt
```

### Running the Application
```bash
python src/main.py
```
Interactive CLI prompts for natural language mandate (e.g., "low volatility portfolio without tech stocks").

### Testing Approach
- Use `test_fmp_historical_prices.ipynb` for isolated component testing
- Test agents individually before integration
- Validate optimization results sum to 1.0 and are non-negative

## Coding Patterns & Conventions

### Agent Implementation
- Each agent is a node function taking `SMAState` and returning `Dict` of state updates
- Use LangChain with GPT-4o-mini for LLM interactions
- Handle errors gracefully with fallback defaults
- Load environment variables via `dotenv` at module level

### Data Flow
- State is immutable; nodes return updates, not mutations
- Use JSON serialization for complex objects in prompts
- Convert numpy arrays to lists for JSON compatibility
- Validate dimensions before optimization (mu.shape[0] == Sigma.shape)

### Error Handling
- Return `{"feedback": error_message}` for recoverable errors
- Use conditional edges for retry logic (e.g., code execution failures)
- Validate weights sum to ~1.0 with tolerance for floating-point errors

### Dependencies & Imports
- Core: langgraph, langchain-openai, pandas, numpy, cvxpy
- API: requests, python-dotenv, pydantic
- Data: finviz, yfinance
- Import project modules with `from src.module import ...` pattern
- Add project root to sys.path in entry points

## Common Tasks

### Adding New Constraints
1. Update `InvestmentConstraints` Pydantic model in `mandate_agent.py`
2. Modify optimizer agent prompt to handle new constraint
3. Update risk model calculations if needed

### Extending Data Sources
1. Add methods to `FMPClient` class
2. Update `data_fetcher_node` to call new methods
3. Ensure data format matches expected Pandas DataFrame structure

### Modifying Optimization
1. Update optimizer agent system prompt with new requirements
2. Ensure generated code follows CVXPY patterns
3. Update executor validation for new output formats

## Integration Points

### External APIs
- **Finviz**: Used for stock screening based on financial metrics
- **YFinance**: Used for downloading historical stock prices
- **OpenAI**: Required `OPENAI_API_KEY` env var for LLM interactions

### File Structure
```
src/
├── main.py              # CLI entry point
├── graph.py             # LangGraph workflow
├── state.py             # State schema
├── agents/              # LLM-powered agents
├── tools/               # Utilities and API clients
└── pyproject.toml       # Package config
```

## Debugging Tips
- Check state updates in workflow nodes
- Validate numpy array shapes before CVXPY operations
- Use isolated execution testing for generated code
- Monitor API rate limits and error responses</content>
<parameter name="filePath">e:\projects\POMS\.github\copilot-instructions.md