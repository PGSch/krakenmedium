#!/usr/bin/env python3
import os
import time
import base64
import hashlib
import hmac
import urllib.parse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class KrakenBot:
    """
    KrakenBot interacts with the Kraken API for placing trades.

    Parameters
    ----------
    None

    Attributes
    ----------
    api_url : str
        Base URL for Kraken API endpoints.
    api_key : str
        API key loaded from environment.
    api_secret : str
        API secret loaded from environment.
    """
    
    def __init__(self):
        """
        Initialize KrakenBot and load API credentials from environment variables.
        """
        self.api_url = "https://api.kraken.com"
        self.api_key = os.environ.get("KRAKEN_API_KEY")
        self.api_secret = os.environ.get("KRAKEN_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret must be set in .env file")
    
    def _get_kraken_signature(self, urlpath, data):
        """
        Create the API-Sign header value for Kraken authenticated requests.

        Parameters
        ----------
        urlpath : str
            URI path of API endpoint (e.g. '/0/private/AddOrder').
        data : dict
            POST data including nonce and parameters.

        Returns
        -------
        str
            Signature string for API-Sign header.
        """
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        # Fix: Ensure API secret has proper base64 padding
        api_secret = self.api_secret
        # Add padding if needed
        padding = len(api_secret) % 4
        if padding:
            api_secret += '=' * (4 - padding)
        
        signature = hmac.new(base64.b64decode(api_secret),
                            message, 
                            hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())
        return sigdigest.decode()
    
    def _kraken_request(self, uri_path, data, headers=None):
        """
        Send a POST request to Kraken private API endpoint with authentication.

        Parameters
        ----------
        uri_path : str
            URI path of the API call.
        data : dict
            Payload including nonce and request parameters.
        headers : dict, optional
            Additional HTTP headers to include.

        Returns
        -------
        dict
            Parsed JSON response from Kraken API.

        Raises
        ------
        Exception
            If the HTTP status is not 200 or Kraken returns an error.
        """
        if not headers:
            headers = {}
            
        headers.update({
            'API-Key': self.api_key,
            'API-Sign': self._get_kraken_signature(uri_path, data)
        })
        
        response = requests.post(
            self.api_url + uri_path, 
            data=data, 
            headers=headers
        )
        
        response_data = response.json()
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response_data.get('error', 'Unknown error')}")
            
        if response_data.get('error'):
            raise Exception(f"API returned error: {response_data['error']}")
            
        return response_data
    
    def limit_buy(self, ticker, price, amount):
        """
        Place a limit buy order on Kraken.

        Parameters
        ----------
        ticker : str
            Asset pair to trade (e.g. 'XBTUSD').
        price : str or float
            Price level to place the buy order.
        amount : str or float
            Quantity to purchase.

        Returns
        -------
        dict
            Kraken API response containing 'txid' and order details.
        """
        data = {
            'nonce': str(int(1000 * time.time())),
            'ordertype': 'limit',
            'type': 'buy',
            'pair': ticker,
            'price': str(price),
            'volume': str(amount)
        }
        
        return self._kraken_request('/0/private/AddOrder', data)
    
    def limit_sell(self, ticker, price, amount):
        """
        Place a limit sell order on Kraken.

        Parameters
        ----------
        ticker : str
            Asset pair to trade (e.g. 'XBTUSD').
        price : str or float
            Price level to place the sell order.
        amount : str or float
            Quantity to sell.

        Returns
        -------
        dict
            Kraken API response containing 'txid' and order details.
        """
        data = {
            'nonce': str(int(1000 * time.time())),
            'ordertype': 'limit',
            'type': 'sell',
            'pair': ticker,
            'price': str(price),
            'volume': str(amount)
        }
        
        return self._kraken_request('/0/private/AddOrder', data)


# Example usage
if __name__ == "__main__":
    try:
        # Create bot instance
        bot = KrakenBot()
        
        # Example (commented out for safety)
        # Buy 0.001 BTC at $40,000 USD
        # result = bot.limit_buy('XBTUSD', 40000, 0.001)
        # print("Buy order placed:", result)
        
        # Sell 0.001 BTC at $45,000 USD
        # result = bot.limit_sell('XBTUSD', 45000, 0.001)
        # print("Sell order placed:", result)
        
        print("Kraken bot initialized successfully!")
        print("Use bot.limit_buy(ticker, price, amount) to place a buy order")
        print("Use bot.limit_sell(ticker, price, amount) to place a sell order")
        
    except Exception as e:
        print(f"Error: {e}")