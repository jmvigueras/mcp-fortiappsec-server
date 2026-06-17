"""
FastMCP server for FortiAppSec (Fortinet WAF as a Service) integration

Run with:
    uvicorn app.server:app --host 0.0.0.0 --port 8000
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from .tools import FortiAppSecTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("FortiAppSec MCP Server")

# Environment variable for API key
ENV_API_KEY = "FORTINET_APPSEC_API_KEY"


def _resolve_api_key(appsec_api_key: str = "") -> str:
    """Resolve API key from parameter or environment variable.

    Priority: explicit parameter > environment variable.
    Raises ValueError if no key is available.
    """
    key = appsec_api_key.strip() if appsec_api_key else ""
    if not key:
        key = os.environ.get(ENV_API_KEY, "").strip()
    if not key:
        raise ValueError(
            "API key is required. Pass appsec_api_key parameter or set "
            "FORTINET_APPSEC_API_KEY environment variable."
        )
    return key


# ===============================
# HEALTH CHECK ENDPOINT
# ===============================


async def health_check(request):
    """Health check endpoint for liveness/readiness probes"""
    return JSONResponse({"status": "healthy", "service": "mcp-fortiappsec-server"})


# ===============================
# WAF APPLICATION TOOLS
# ===============================


@mcp.tool()
def waf_list_applications(
    appsec_api_key: str = "",
) -> str:
    """List all WAF applications in FortiAppSec.

    Args:
        appsec_api_key: FortiAppSec API key (optional if FORTINET_APPSEC_API_KEY env var is set)
    """
    api_key = _resolve_api_key(appsec_api_key)
    result = FortiAppSecTools.list_waf_applications(api_key)
    return json.dumps(result, indent=2)


@mcp.tool()
def waf_get_application(
    app_id: str,
    appsec_api_key: str = "",
) -> str:
    """Get details of a specific WAF application in FortiAppSec.

    Args:
        app_id: Application ID to retrieve
        appsec_api_key: FortiAppSec API key (optional if FORTINET_APPSEC_API_KEY env var is set)
    """
    api_key = _resolve_api_key(appsec_api_key)
    result = FortiAppSecTools.get_waf_application(api_key, app_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def waf_create_application(
    app_name: str,
    domain_name: str,
    server_address: str,
    appsec_api_key: str = "",
    server_port: int = 80,
    extra_domains: str = "",
    custom_port_http: int = 80,
    custom_port_https: int = 443,
    cdn_status: int = 0,
    region: str = "eu-west-1",
    platform: str = "AWS",
    block_mode: int = 1,
    service: str = "http,https",
    server_type: str = "http",
    server_country: str = "Ireland",
    head_availability: int = 1,
    head_status_code: int = 404,
    template_id: str = "355e3ce6-0d0e-485f-acf5-a37ecd91cd1b",
) -> str:
    """Create a new WAF application in FortiAppSec.

    Args:
        app_name: Application name
        domain_name: Primary domain name (e.g., myapp.example.com)
        server_address: Backend server address/DNS name
        appsec_api_key: FortiAppSec API key (optional if FORTINET_APPSEC_API_KEY env var is set)
        server_port: Backend server port (default: 80)
        extra_domains: Additional domains (comma-separated, empty for none)
        custom_port_http: HTTP listening port (default: 80)
        custom_port_https: HTTPS listening port (default: 443)
        cdn_status: CDN status (0=disabled, 1=enabled)
        region: Cloud region (default: eu-west-1)
        platform: Platform type (default: AWS)
        block_mode: Block mode (0=monitor, 1=block)
        service: Services (comma-separated, default: http,https)
        server_type: Server type (http or https)
        server_country: Server country (default: Ireland)
        head_availability: Health check availability (default: 1)
        head_status_code: Expected health check status code (default: 404)
        template_id: Template ID for the application
    """
    # Resolve API key
    api_key = _resolve_api_key(appsec_api_key)

    # Convert comma-separated strings to lists
    extra_domains_list = [d.strip() for d in extra_domains.split(",") if d.strip()] if extra_domains else []
    service_list = [s.strip() for s in service.split(",") if s.strip()]

    result = FortiAppSecTools.create_waf_application(
        api_key=api_key,
        app_name=app_name,
        domain_name=domain_name,
        server_address=server_address,
        server_port=server_port,
        extra_domains=extra_domains_list,
        custom_port_http=custom_port_http,
        custom_port_https=custom_port_https,
        cdn_status=cdn_status,
        region=region,
        platform=platform,
        block_mode=block_mode,
        service=service_list,
        server_type=server_type,
        server_country=server_country,
        head_availability=head_availability,
        head_status_code=head_status_code,
        template_id=template_id,
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def waf_delete_application(
    app_id: str,
    appsec_api_key: str = "",
) -> str:
    """Delete a WAF application from FortiAppSec.

    Args:
        app_id: Application ID to delete
        appsec_api_key: FortiAppSec API key (optional if FORTINET_APPSEC_API_KEY env var is set)
    """
    api_key = _resolve_api_key(appsec_api_key)
    result = FortiAppSecTools.delete_waf_application(api_key, app_id)
    return json.dumps(result, indent=2)


# ===============================
# WAF TEMPLATE TOOLS
# ===============================


@mcp.tool()
def waf_list_templates(
    appsec_api_key: str = "",
) -> str:
    """List WAF templates available in FortiAppSec.

    Args:
        appsec_api_key: FortiAppSec API key (optional if FORTINET_APPSEC_API_KEY env var is set)
    """
    api_key = _resolve_api_key(appsec_api_key)
    result = FortiAppSecTools.list_waf_templates(api_key)
    return json.dumps(result, indent=2)


# Create the ASGI app with health check endpoint mounted alongside MCP
mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app):
    """Manage MCP server lifespan within the parent Starlette app"""
    async with mcp_app.router.lifespan_context(mcp_app):
        yield


app = Starlette(
    routes=[
        Route("/health", health_check),
        Mount("/", app=mcp_app),
    ],
    lifespan=lifespan,
)
