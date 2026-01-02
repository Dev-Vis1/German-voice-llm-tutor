import requests
import json
from typing import Optional

def ask_ollama(
    prompt: str, 
    model: str = "llama3.1:8b", 
    base_url: str = "http://localhost:11434",
    timeout: int = 60  # Reduced timeout for better reliability
) -> str:
    """
    Send prompt to Ollama and return response.
    
    Args:
        prompt: The text prompt to send
        model: Model name (mistral, llama2, etc.) 
        base_url: Ollama server URL
        timeout: Request timeout in seconds
    
    Returns:
        String response from the model
    """
    try:
        url = f"{base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False  # Get complete response at once
        }
        
        response = requests.post(
            url, 
            json=payload, 
            timeout=timeout  # Use configurable timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if "response" not in result:
            raise Exception(f"Invalid response format: {result}")
        
        return result["response"].strip()
    
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Make sure Ollama is running on localhost:11434")
    
    except requests.exceptions.Timeout:
        raise Exception("Ollama request timed out. Try a shorter prompt or different model.")
    
    except Exception as e:
        raise Exception(f"Ollama client error: {str(e)}")

def list_ollama_models(base_url: str = "http://localhost:11434") -> list:
    """
    Get list of available models from Ollama.
    
    Returns:
        List of model names
    """
    try:
        url = f"{base_url}/api/tags"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get models: {response.status_code}")
        
        result = response.json()
        return [model["name"] for model in result.get("models", [])]
    
    except Exception as e:
        print(f"Warning: Could not get model list: {e}")
        return ["mistral"]  # Default fallback

def check_ollama_status(base_url: str = "http://localhost:11434") -> bool:
    """
    Check if Ollama is running and accessible.
    
    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# Test function
if __name__ == "__main__":
    # Test Ollama connection
    print("Testing Ollama connection...")
    
    if check_ollama_status():
        print("✓ Ollama is running")
        
        models = list_ollama_models()
        print(f"Available models: {models}")
        
        # Test simple prompt
        try:
            test_prompt = "Say hello in German."
            response = ask_ollama(test_prompt)
            print(f"Test response: {response}")
        except Exception as e:
            print(f"✗ Test failed: {e}")
    else:
        print("✗ Ollama is not running. Start it with: ollama serve")