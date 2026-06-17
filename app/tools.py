"""
FortiAppSec Tools Implementation for MCP Server
"""

import logging
from typing import Any, Dict, List, Optional

from .appsec_client import FortiAppSecClient

logger = logging.getLogger(__name__)


class FortiAppSecTools:
    """FortiAppSec tools implementation"""

    @staticmethod
    def create_client(api_key: str, base_url: str = "https://api.appsec.fortinet.com") -> FortiAppSecClient:
        """Create FortiAppSec client instance"""
        return FortiAppSecClient(api_key, base_url)

    @staticmethod
    def list_waf_applications(api_key: str) -> Dict[str, Any]:
        """Get list of all WAF applications"""
        try:
            client = FortiAppSecTools.create_client(api_key)
            result = client.get("/v2/waf/apps")

            if result.get("status") == "error":
                return {
                    "success": False,
                    "message": result.get("message", "Unknown error"),
                    "data": [],
                }

            # The API may return data directly or in a 'data' key
            data = result.get("data", result)
            if isinstance(data, dict) and "http_status" in data:
                # Remove internal http_status from the response
                data = {k: v for k, v in data.items() if k != "http_status"}

            return {
                "success": True,
                "message": "WAF applications retrieved",
                "data": data,
            }

        except Exception as e:
            logger.error(f"Error listing WAF applications: {e}")
            return {
                "success": False,
                "message": f"Error listing WAF applications: {str(e)}",
                "data": [],
            }

    @staticmethod
    def get_waf_application(api_key: str, app_id: str) -> Dict[str, Any]:
        """Get details of a specific WAF application"""
        try:
            client = FortiAppSecTools.create_client(api_key)
            result = client.get(f"/v2/waf/apps/{app_id}")

            if result.get("status") == "error":
                return {
                    "success": False,
                    "message": result.get("message", "Unknown error"),
                    "data": {},
                }

            # Remove internal http_status from the response
            data = {k: v for k, v in result.items() if k != "http_status"}

            return {
                "success": True,
                "message": f"WAF application '{app_id}' retrieved",
                "data": data,
            }

        except Exception as e:
            logger.error(f"Error getting WAF application: {e}")
            return {
                "success": False,
                "message": f"Error getting WAF application: {str(e)}",
                "data": {},
            }

    @staticmethod
    def create_waf_application(
        api_key: str,
        app_name: str,
        domain_name: str,
        server_address: str,
        server_port: int = 80,
        extra_domains: Optional[List[str]] = None,
        custom_port_http: int = 80,
        custom_port_https: int = 443,
        cdn_status: int = 0,
        region: str = "eu-west-1",
        platform: str = "AWS",
        block_mode: int = 1,
        service: Optional[List[str]] = None,
        server_type: str = "http",
        server_country: str = "Ireland",
        head_availability: int = 1,
        head_status_code: int = 404,
        template_id: str = "355e3ce6-0d0e-485f-acf5-a37ecd91cd1b",
    ) -> Dict[str, Any]:
        """Create a new WAF application in FortiAppSec"""
        try:
            if extra_domains is None:
                extra_domains = []
            if service is None:
                service = ["http", "https"]

            client = FortiAppSecTools.create_client(api_key)

            payload = {
                "app_name": app_name,
                "domain_name": domain_name,
                "extra_domains": extra_domains,
                "custom_port": {
                    "http": custom_port_http,
                    "https": custom_port_https,
                },
                "cdn_status": cdn_status,
                "region": region,
                "platform": platform,
                "block_mode": block_mode,
                "service": service,
                "server_address": server_address,
                "server_port": server_port,
                "server_type": server_type,
                "server_country": server_country,
                "head_availability": head_availability,
                "head_status_code": head_status_code,
                "template_id": template_id,
            }

            result = client.post("/v2/waf/apps", payload)

            if result.get("status") == "error":
                return {
                    "success": False,
                    "message": result.get("message", "Unknown error"),
                    "data": {},
                }

            # Remove internal http_status from the response
            data = {k: v for k, v in result.items() if k != "http_status"}

            return {
                "success": True,
                "message": f"WAF application '{app_name}' created successfully",
                "data": data,
            }

        except Exception as e:
            logger.error(f"Error creating WAF application: {e}")
            return {
                "success": False,
                "message": f"Error creating WAF application: {str(e)}",
                "data": {},
            }

    @staticmethod
    def delete_waf_application(api_key: str, app_id: str) -> Dict[str, Any]:
        """Delete a WAF application"""
        try:
            client = FortiAppSecTools.create_client(api_key)
            result = client.delete(f"/v2/waf/apps/{app_id}")

            if result.get("status") == "error":
                return {
                    "success": False,
                    "message": result.get("message", "Unknown error"),
                }

            return {
                "success": True,
                "message": f"WAF application '{app_id}' deleted successfully",
            }

        except Exception as e:
            logger.error(f"Error deleting WAF application: {e}")
            return {
                "success": False,
                "message": f"Error deleting WAF application: {str(e)}",
            }

    @staticmethod
    def list_waf_templates(api_key: str) -> Dict[str, Any]:
        """List WAF templates available"""
        try:
            client = FortiAppSecTools.create_client(api_key)
            result = client.get("/v2/waf/template")

            if result.get("status") == "error":
                return {
                    "success": False,
                    "message": result.get("message", "Unknown error"),
                    "data": [],
                }

            # The API may return data directly or in a 'data' key
            data = result.get("data", result)
            if isinstance(data, dict) and "http_status" in data:
                data = {k: v for k, v in data.items() if k != "http_status"}

            return {
                "success": True,
                "message": "WAF templates retrieved",
                "data": data,
            }

        except Exception as e:
            logger.error(f"Error listing WAF templates: {e}")
            return {
                "success": False,
                "message": f"Error listing WAF templates: {str(e)}",
                "data": [],
            }
