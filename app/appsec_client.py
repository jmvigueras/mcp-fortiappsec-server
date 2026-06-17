"""
FortiAppSec API Client for MCP Server
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF = 1.0  # seconds


class FortiAppSecClient:
    """FortiAppSec API client for MCP server"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.appsec.fortinet.com",
        timeout: int = 30,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
    ):
        """
        Initialize FortiAppSec API client

        Args:
            api_key: API key for authentication
            base_url: Base URL for FortiAppSec API
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for transient failures
            retry_backoff: Base backoff time in seconds between retries
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.session = requests.Session()

        # Set headers
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": api_key,
            }
        )

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to FortiAppSec API with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (should start with /)
            data: Request data for POST/PUT

        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url, json=data, timeout=self.timeout
                    )
                elif method.upper() == "PUT":
                    response = self.session.put(
                        url, json=data, timeout=self.timeout
                    )
                elif method.upper() == "DELETE":
                    response = self.session.delete(
                        url, timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Log request details
                logger.info(
                    f"{method.upper()} {endpoint} - Status: {response.status_code}"
                )

                # Handle empty responses (e.g., 204 No Content)
                if response.status_code == 204 or not response.content:
                    return {
                        "success": True,
                        "message": "Operation completed successfully",
                        "http_status": response.status_code,
                    }

                # Raise for HTTP errors
                response.raise_for_status()

                # Parse JSON response
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    result = {
                        "raw_response": response.text[:500],
                    }

                # Add HTTP status code to result
                if isinstance(result, dict):
                    result["http_status"] = response.status_code
                else:
                    # If the API returns a list, wrap it
                    result = {
                        "data": result,
                        "http_status": response.status_code,
                    }

                return result

            except requests.exceptions.HTTPError as e:
                # Extract error details from the response
                error_msg = f"HTTP error {response.status_code}"
                try:
                    error_detail = response.json()
                    if "message" in error_detail:
                        error_msg += f": {error_detail['message']}"
                    elif "error" in error_detail:
                        error_msg += f": {error_detail['error']}"
                    elif "detail" in error_detail:
                        error_msg += f": {error_detail['detail']}"
                except (json.JSONDecodeError, AttributeError):
                    error_msg += f": {response.text[:200]}"

                # Don't retry client errors (4xx)
                if response.status_code < 500:
                    return {
                        "status": "error",
                        "message": error_msg,
                        "http_status": response.status_code,
                    }

                # Retry server errors (5xx)
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_backoff * (2**attempt)
                    logger.warning(
                        f"Server error on attempt {attempt + 1}/{self.max_retries}, "
                        f"retrying in {wait_time}s: {error_msg}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Request failed after {self.max_retries} attempts: {error_msg}"
                    )
                    return {
                        "status": "error",
                        "message": error_msg,
                        "http_status": response.status_code,
                    }

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_backoff * (2**attempt)
                    logger.warning(
                        f"Connection error on attempt {attempt + 1}/{self.max_retries}, "
                        f"retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Connection failed after {self.max_retries} attempts: {e}"
                    )

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_backoff * (2**attempt)
                    logger.warning(
                        f"Timeout on attempt {attempt + 1}/{self.max_retries}, "
                        f"retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Request timed out after {self.max_retries} attempts: {e}"
                    )

            except requests.exceptions.RequestException as e:
                # Non-retryable request errors
                logger.error(f"Request failed: {e}")
                return {
                    "status": "error",
                    "message": f"Request failed: {str(e)}",
                    "http_status": 0,
                }

        # All retries exhausted
        return {
            "status": "error",
            "message": f"Request failed after {self.max_retries} attempts: {str(last_exception)}",
            "http_status": 0,
        }

    def get(self, endpoint: str) -> Dict[str, Any]:
        """GET request"""
        return self._make_request("GET", endpoint)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request"""
        return self._make_request("POST", endpoint, data)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT request"""
        return self._make_request("PUT", endpoint, data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request"""
        return self._make_request("DELETE", endpoint)
