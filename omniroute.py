import requests
import json
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Secure configurations loaded from environment
BASE_URL = os.environ.get("OMNIROUTE_BASE_URL", "https://localhost:20128")
PASSWORD = os.environ.get("OMNIROUTE_PASSWORD")

if not PASSWORD:
    logging.critical("OMNIROUTE_PASSWORD environment variable is not set. Refusing to run.")
    sys.exit(1)

def get_auth_token():
    """Logs into the local dashboard to get a session/bearer token."""
    login_url = f"{BASE_URL}/api/auth/login"
    payload = {"password": PASSWORD}
    try:
        # verify=False for localhost HTTPS development, but normally should be True
        response = requests.post(login_url, json=payload, verify=False)
        response.raise_for_status()
        return response.json().get("token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to OmniRoute. Is it running? Error: {e}")
        sys.exit(1)

def configure_all_free_providers():
    token = get_auth_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Fetch already connected providers to ensure idempotency
    try:
        active_res = requests.get(f"{BASE_URL}/api/providers", headers=headers, verify=False)
        active_res.raise_for_status()
        active_ids = {p.get("id") for p in active_res.json().get("connections", [])}
    except requests.exceptions.RequestException as e:
        logging.warning(f"Could not fetch active providers for idempotency check: {e}")
        active_ids = set()

    # Fetch the catalog of available free tier system modules
    catalog_url = f"{BASE_URL}/api/providers/catalog/free-tiers"
    try:
        catalog_res = requests.get(catalog_url, headers=headers, verify=False)
        catalog_res.raise_for_status()
        free_providers = catalog_res.json().get("providers", [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not fetch provider catalog: {e}")
        sys.exit(1)

    logging.info(f"Found {len(free_providers)} free providers. Starting automated setup...")

    # Loop through each provider and enable them natively
    for provider in free_providers:
        provider_id = provider.get("id")
        provider_name = provider.get("name")
        
        if provider_id in active_ids:
            logging.info(f"Skipping {provider_name} ({provider_id}) - Already linked.")
            continue
            
        connect_url = f"{BASE_URL}/api/providers/connect"
        payload = {
            "providerId": provider_id,
            "config": {} 
        }
        
        try:
            res = requests.post(connect_url, json=payload, headers=headers, verify=False)
            if res.status_code in [200, 201]:
                logging.info(f"Successfully linked: {provider_name} ({provider_id})")
            else:
                logging.warning(f"Failed to link {provider_name}: {res.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error linking {provider_name}: {e}")

    # Trigger system validation test across all newly registered streams
    logging.info("Setup complete. Initializing multi-provider latency test...")
    try:
        test_res = requests.post(f"{BASE_URL}/api/providers/test-all", headers=headers, verify=False)
        test_res.raise_for_status()
        logging.info("Test complete! Check your terminal console for the live fallback routing metrics.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not automatically trigger health test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    configure_all_free_providers()
