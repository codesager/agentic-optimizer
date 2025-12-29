# Setup Instructions for Agentic Optimizer

This guide will help you set up the Agentic Optimizer environment on your local machine.

## Prerequisites

- **Python 3.12** or higher.
- **OpenAI API Key**: You need a valid API key from OpenAI to power the agents.

## 1. System Preparation

Ensure Python is installed and added to your system PATH.

```bash
python --version
# Should output Python 3.12.x or higher
```

## 2. Environment Variables

Create a `.env` file in the root directory of the project. This file is used to store sensitive configuration.

**File:** `.env`
```env
OPENAI_API_KEY=sk-your_api_key_here
```

## 3. Virtual Environment & Dependencies

It is recommended to use a virtual environment to manage dependencies.

### Windows

**Option 1: Automatic Setup**
Run the included batch script:
```cmd
setup_env.bat
```

**Option 2: Manual Setup**
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### macOS / Linux

**Option 1: Automatic Setup**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Option 2: Manual Setup**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

> **Note**: If `requirements.txt` is missing or you prefer using modern tools, you can install the core dependencies directly:
> ```bash
> pip install langchain-openai langgraph finvizfinance pandas numpy scipy scikit-learn python-dotenv
> ```

## 4. Running the Application

1.  **Activate your virtual environment** (if not already active):
    *   Windows: `venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`

2.  **Run the entry point:**
    ```bash
    python src/main.py
    ```

3.  **Enter a mandate** when prompted:
    *   *Example:* "Construct a portfolio of large cap tech stocks with minimized volatility."

## Troubleshooting

- **Import Errors**: If you see errors about missing modules (`langgraph`, `langchain`, etc.), ensure you have activated the virtual environment and ran the pip install command.
- **API Key Errors**: Ensure your `.env` file is in the root directory and contains a valid `OPENAI_API_KEY`.
