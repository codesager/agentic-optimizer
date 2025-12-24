# Setup Instructions for POMS Project

## Prerequisites

You need Python 3.8 or higher installed on your system.

### Check Python Installation

Open a terminal/command prompt and run:
```bash
python --version
```

If Python is not found, you have a few options:

1. **Install Python from python.org**: Download and install from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Use an existing Python installation**: If you have Python installed but it's not in PATH, you can:
   - Use the full path to Python
   - Or add Python to your system PATH

## Setup Virtual Environment

### On Windows:

**Option 1: Using the batch script**
```bash
setup_env.bat
```

**Option 2: Manual setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### On Linux/Mac:

**Option 1: Using the shell script**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

**Option 2: Manual setup**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

## Activating the Virtual Environment

After setup, whenever you want to work on the project:

**Windows:**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt when the environment is active.

## Running the Application

Once the virtual environment is activated and dependencies are installed:

```bash
python src/main.py
```

## Troubleshooting

### Python not found
- Ensure Python is installed and added to your system PATH
- Try using `python3` instead of `python`
- On Windows, try using `py` launcher: `py -m venv venv`

### Virtual environment creation fails
- Make sure you have write permissions in the project directory
- Try deleting any existing `venv` folder and recreating it
- Ensure you have enough disk space

### Package installation fails
- Make sure your internet connection is working
- Try upgrading pip: `python -m pip install --upgrade pip`
- Some packages may require system-level dependencies (especially on Linux)

