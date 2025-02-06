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
from functools import lru_cache
import hashlib

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

@lru_cache(maxsize=128)  # Cache up to 128 unique prompts
def comunicate_with_llm_cached(prompt: str, **kwargs) -> str:
    """
    This function communicates with a language model (LLM) and caches the responses to improve efficiency. 
    It uses the MD5 hash of the prompt as the cache key to handle large inputs. If the response for a given 
    prompt is already cached, it returns the cached response. Otherwise, it makes an API call to get the response 
    from the LLM and caches the result.
    Args:
        prompt (str): The input prompt to be sent to the LLM.
        **kwargs: Additional keyword arguments for customization.
            - api_key (str): The API key for authentication. Defaults to a global API_KEY.
            - model (str): The model to be used for the LLM. Defaults to "meta-llama/llama-3.2-1b-instruct:free".
            - temperature (float): The temperature setting for the LLM. Defaults to 1.
            - max_tokens (int): The maximum number of tokens in the response. Defaults to 1024.
            - api_url (str): The URL of the API endpoint. Defaults to a global API_URL.
            - timeout (int): The timeout for the API request in seconds. Defaults to 30.
    Returns:
        str: The response from the LLM, either from the cache or from the API call.
    Raises:
        requests.exceptions.RequestException: If the API request fails.
    Notes:
        - The cache is implemented using a dictionary stored in the function's cache_info attribute.
        - The cache_info attribute must be initialized with a 'hits' dictionary before using this function.
    """
    cache_key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
    logging.debug(f"Cache key: {cache_key}")
    
    # Check cache first
    if cache_key in comunicate_with_llm_cached.cache_info().hits:
        logging.info("Returning cached response")
        return comunicate_with_llm_cached.cache_info().hits[cache_key]
    
    # Proceed with API call if not in cache
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
        result = response.json()['choices'][0]['message']['content'].strip()
        
        # Cache the result
        comunicate_with_llm_cached.cache_info().hits[cache_key] = result
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {str(e)}")
        return None    

def comunicate_with_llm(prompt, **kwargs):
    """
    Communicates with a language model (LLM) API using the provided prompt and optional parameters.
    Args:
        prompt (str): The input prompt to send to the LLM.
        **kwargs: Optional keyword arguments to customize the API request:
            - api_key (str): The API key for authentication. Defaults to a global API_KEY.
            - model (str): The model identifier to use. Defaults to "meta-llama/llama-3.2-1b-instruct:free".
            - temperature (float): The sampling temperature. Defaults to 1.
            - max_tokens (int): The maximum number of tokens to generate. Defaults to 1024.
            - api_url (str): The URL of the API endpoint. Defaults to a global API_URL.
            - timeout (int): The request timeout in seconds. Defaults to 30.
    Returns:
        str: The generated response from the LLM, or None if the request failed.
    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
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
    """
    Main function to handle command-line interface for LLM communication.
    This function sets up argument parsing for various input options, validates
    the provided API key, reads the input prompt (either from command-line or file),
    and communicates with the LLM API. The result is either printed to the console
    or saved to a specified output file.
    Arguments:
        prompt (list of str): Input prompt text (or use -f for file input).
        -f, --file (Path): Read prompt from text file.
        -o, --output (Path): Save output to file.
        -m, --model (str): Model identifier (default: "meta-llama/llama-3.2-1b-instruct:free").
        -t, --temperature (float): Sampling temperature (default: 1.0).
        --api-key (str): OpenRouter API key (default: API_KEY).
        --api-url (str): API endpoint URL (default: API_URL).
        -v, --verbose (bool): Enable verbose logging.
    Raises:
        SystemExit: If no valid API key is provided, if there is an error reading
                    the input file, if no input prompt is provided, or if there is
                    an error writing the output file.
    """
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
    result = comunicate_with_llm_cached(
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