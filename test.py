import requests
import time
import concurrent.futures

# LLM Server URL
API_URL = "http://localhost:11434/v1/chat/completions"

# Model & Settings
MODELS = ["mistral:latest", "llama3:latest"]
MAX_TOKENS = 300
REQUEST_TIMEOUT = 60  # Set timeout for each request
CONCURRENT_REQUESTS = 5  # Adjust based on system load

# Prompt for entity extraction
INPUT_TEXT = "Extract named entities from: The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates."

def test_model(model_name):
    """Send a request to the LLM and measure response time."""
    data = {
        "model": model_name,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "system", "content": INPUT_TEXT}]
    }

    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=data, timeout=REQUEST_TIMEOUT)
        elapsed_time = time.time() - start_time
        
        # Print results
        print(f"\nModel: {model_name}")
        print(f"Response Time: {elapsed_time:.2f} seconds")
        print("Response:", response.json())
        
        return elapsed_time
    except requests.exceptions.Timeout:
        print(f"\nModel: {model_name} - Request Timed Out!")
        return None
    except Exception as e:
        print(f"\nModel: {model_name} - Error: {e}")
        return None

def run_concurrent_tests():
    """Run multiple concurrent requests to test LLM performance."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        results = list(executor.map(test_model, MODELS))

    print("\n=== Final Results ===")
    for i, model in enumerate(MODELS):
        print(f"{model}: {results[i]} sec")

# Run the test
run_concurrent_tests()
