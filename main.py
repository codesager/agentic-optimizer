
import sys
import os
from pathlib import Path

# Add the project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.main import main
except ImportError as e:
    print(f"Error importing src.main: {e}")
    print("Ensure you are running this script from the project root.")
    sys.exit(1)

if __name__ == "__main__":
    main()
