# Agentic Optimizer

The **Agentic Optimizer** is a sophisticated multi-agent system designed to automate the customization of Separately Managed Accounts (SMAs). It leverages a team of specialized AI agents to interpret natural language investment mandates, screen the market, model risk, and mathematically optimize portfolios to meet specific user goals.

Built with **LangGraph**, **LangChain**, and **OpenAI**, this system orchestrates a complex workflow from raw user input to a final, approved portfolio.

## 🚀 Key Features

- **Natural Language Processing**: Simply state your investment goals (e.g., *"I want a low volatility portfolio excluding the Technology sector"*).
- **Multi-Agent Architecture**:
  - **Mandate Agent**: Interprets user requirements and extracts structured constraints.
  - **Screener Agent**: Filters the stock universe using **Finviz** based on fundamental criteria.
  - **Pricing Agent**: Fetches historical price data for the selected universe.
  - **Risk Model Agent**: Calculates expected returns and covariance matrices.
  - **Optimizer Agent**: Writes and executes custom Python code (using `scipy`/`cvxpy`) to solve the optimization problem.
  - **Reviewer Agent**: Critically assesses the generated portfolio against the original mandate.
- **Robust Workflow**: expertly managed state transitions, error handling, and auto-retries for optimization failures.
- **Transparent Output**: Provides detailed feedback, activity logs, and final portfolio weights.

## 🛠️ Architecture

The system follows a directed graph workflow:

1.  **Parse Mandate**: User input -> Structured Constraints.
2.  **Screen Stocks**: Constraints -> List of Tickers.
3.  **Fetch Prices**: Tickers -> Historical Data.
4.  **Calculate Risk Model**: Data -> Returns ($\mu$) & Covariance ($\Sigma$).
5.  **Generate Optimizer Code**: Risk Model + Constraints -> Python Optimization Script.
6.  **Execute Code**: Script -> Portfolio Weights.
7.  **Review Portfolio**: Final Portfolio -> Approval/Feedback.

## 📦 Installation & Setup

Please refer to the [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) file for detailed steps on setting up your environment and dependencies.

## 🏃 Usage

Once set up, run the application from the project root:

```bash
python src/main.py
```

Follow the interactive prompt to enter your investment mandate.
