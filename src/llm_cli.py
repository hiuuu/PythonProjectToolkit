#!/usr/bin/env python3
"""
LLM Command-Line Interface Tool
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv  # pip install requests python-dotenv
import requests

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")

def configure_logging(verbose=False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=level
    )

def comunicate_with_llm(prompt, **kwargs):
    """Modified version with enhanced error handling"""
    headers = {
        "Authorization": f"Bearer {kwargs.get('api_key', API_KEY)}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": kwargs.get('model', "meta-llama/llama-3.2-1b-instruct:free"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": kwargs.get('temperature', 1),
        "max_tokens": kwargs.get('max_tokens', 1024)
    }

    try:
        response = requests.post(
            kwargs.get('api_url', API_URL),
            headers=headers,
            json=data,
            timeout=kwargs.get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="CLI Interface for LLM Communication",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input arguments
    parser.add_argument(
        'prompt', 
        nargs='*',
        help="Input prompt text (or use -f for file input)"
    )
    parser.add_argument(
        '-f', '--file',
        type=Path,
        help="Read prompt from text file"
    )
    
    # Output arguments
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help="Save output to file"
    )
    
    # Model parameters
    parser.add_argument(
        '-m', '--model',
        default="meta-llama/llama-3.2-1b-instruct:free",
        help="Model identifier"
    )
    parser.add_argument(
        '-t', '--temperature',
        type=float,
        default=1.0,
        help="Sampling temperature"
    )
    
    # API configuration
    parser.add_argument(
        '--api-key',
        default=API_KEY,
        help="OpenRouter API key"
    )
    parser.add_argument(
        '--api-url',
        default=API_URL,
        help="API endpoint URL"
    )
    
    # Runtime options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    configure_logging(args.verbose)

    # Validate API key
    if args.api_key == "your-api-key-here":
        logging.error("No valid API key provided!")
        logging.info("Set OPENROUTER_API_KEY in environment or use --api-key")
        sys.exit(1)

    # Read input
    if args.file:
        try:
            with open(args.file, 'r') as f:
                prompt = f.read()
        except IOError as e:
            logging.error(f"File read error: {str(e)}")
            sys.exit(1)
    else:
        prompt = ' '.join(args.prompt)
    
    if not prompt:
        logging.error("No input prompt provided!")
        parser.print_help()
        sys.exit(1)

    # Execute LLM request
    result = comunicate_with_llm(
        prompt,
        model=args.model,
        temperature=args.temperature,
        api_key=args.api_key,
        api_url=args.api_url
    )

    # Handle output
    if result:
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(result)
                logging.info(f"Output saved to {args.output}")
            except IOError as e:
                logging.error(f"File write error: {str(e)}")
                sys.exit(1)
        else:
            print(result)
    else:
        logging.error("No response received from the API")
        sys.exit(1)

if __name__ == "__main__":
    main()
    
    
"""
USAGE

# Direct text input
llm_cli.py "Explain quantum computing in simple terms"

# File input
llm_cli.py -f input.txt

# Piped input
cat input.txt | llm_cli.py -

# Save to file
llm_cli.py "Explain REST APIs" -o output.md

# Custom model selection
llm_cli.py -m "google/palm-2" "Explain machine learning"

# Temperature control
llm_cli.py -t 0.7 "Creative story about robots"

# Custom API endpoint
llm_cli.py --api-url "https://alternative-api.example.com/v1" ...

# Runtime API key
llm_cli.py --api-key $CUSTOM_KEY "Secret query"


llm_cli.py -v "Debugging demo"  # Shows detailed logs

"""