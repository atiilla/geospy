# __main__.py

import sys
import logging
from typing import NoReturn

def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.WARNING,
        format='%(levelname)s: %(message)s'
    )

def main() -> NoReturn:
    """Main entry point with proper error handling."""
    setup_logging()
    
    try:
        from .cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Error: Missing required module: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error: An unexpected error occurred. Please check your input and try again.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
