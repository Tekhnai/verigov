import sys
import os
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cnpj_fetch(cnpj):
    url = f"https://publica.cnpj.ws/cnpj/{cnpj}"
    headers = {"User-Agent": "verigov/1.0", "Accept": "application/json, */*"}
    timeout = httpx.Timeout(30.0, connect=10.0)

    logger.info(f"Attempting to fetch {url}...")
    
    try:
        # Replicating the logic from receita.py
        with httpx.Client(
            timeout=timeout, headers=headers, follow_redirects=True, http2=True
        ) as client:
            resp = client.get(url)
            logger.info(f"Status Code: {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            logger.info("Successfully fetched data.")
            # print(data) # Commented out to avoid clutter
            return True
    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP error: {exc.response.status_code} - {exc.response.text}")
    except Exception as exc:
        logger.error(f"An error occurred: {exc}")
    return False

if __name__ == "__main__":
    # Google CNPJ for testing
    test_cnpj = "06990590000123" 
    if test_cnpj_fetch(test_cnpj):
        print("Test passed!")
        sys.exit(0)
    else:
        print("Test failed!")
        sys.exit(1)
