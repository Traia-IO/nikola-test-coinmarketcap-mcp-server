#!/usr/bin/env python3
"""
Nikola Test CoinMarketCap MCP Server - FastMCP with D402 Transport Wrapper

Uses FastMCP from official MCP SDK with D402MCPTransport wrapper for HTTP 402.

Architecture:
- FastMCP for tool decorators and Context objects
- D402MCPTransport wraps the /mcp route for HTTP 402 interception
- Proper HTTP 402 status codes (not JSON-RPC wrapped)

Generated from OpenAPI: https://coinmarketcap.com/api/documentation/v1/

Environment Variables:
- NIKOLA_TEST_COINMARKETCAP_API_KEY: Server's internal API key (for paid requests)
- SERVER_ADDRESS: Payment address (IATP wallet contract)
- MCP_OPERATOR_PRIVATE_KEY: Operator signing key
- D402_TESTING_MODE: Skip facilitator (default: true)
"""

import os
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union
from datetime import datetime

import requests
from retry import retry
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nikola-test-coinmarketcap_mcp')

# FastMCP from official SDK
from mcp.server.fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# D402 payment protocol - using Starlette middleware
from traia_iatp.d402.starlette_middleware import D402PaymentMiddleware
from traia_iatp.d402.mcp_middleware import require_payment_for_tool, get_active_api_key
from traia_iatp.d402.payment_introspection import extract_payment_configs_from_mcp
from traia_iatp.d402.types import TokenAmount, TokenAsset, EIP712Domain

# Configuration
STAGE = os.getenv("STAGE", "MAINNET").upper()
PORT = int(os.getenv("PORT", "8000"))
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
if not SERVER_ADDRESS:
    raise ValueError("SERVER_ADDRESS required for payment protocol")

API_KEY = os.getenv("NIKOLA_TEST_COINMARKETCAP_API_KEY")
if not API_KEY:
    logger.warning(f"⚠️  NIKOLA_TEST_COINMARKETCAP_API_KEY not set - payment required for all requests")

logger.info("="*80)
logger.info(f"Nikola Test CoinMarketCap MCP Server (FastMCP + D402 Wrapper)")
logger.info(f"API: https://pro-api.coinmarketcap.com")
logger.info(f"Payment: {SERVER_ADDRESS}")
logger.info(f"API Key: {'✅' if API_KEY else '❌ Payment required'}")
logger.info("="*80)

# Create FastMCP server
mcp = FastMCP("Nikola Test CoinMarketCap MCP Server", host="0.0.0.0")

logger.info(f"✅ FastMCP server created")

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================
# Tool implementations will be added here by endpoint_implementer_crew
# Each tool will use the @mcp.tool() and @require_payment_for_tool() decorators


# D402 Payment Middleware
# The HTTP 402 payment protocol middleware is already configured in the server initialization.
# It's imported from traia_iatp.d402.mcp_middleware and auto-detects configuration from:
# - PAYMENT_ADDRESS or EVM_ADDRESS: Where to receive payments
# - EVM_NETWORK: Blockchain network (default: base-sepolia)
# - DEFAULT_PRICE_USD: Price per request (default: $0.001)
# - NIKOLA_TEST_COINMARKETCAP_API_KEY: Server's internal API key for payment mode
#
# All payment verification logic is handled by the traia_iatp.d402 module.
# No custom implementation needed!


# API Endpoint Tool Implementations

@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Price Conversion v2"

)
async def getv2toolspriceconversion(
    context: Context,
    amount: Optional[str] = None,
    id: Optional[str] = None,
    symbol: Optional[str] = None,
    time: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Price Conversion v2

    Generated from OpenAPI endpoint: GET /v2/tools/price-conversion

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        amount: An amount of currency to convert. Example: 10.43 (optional)
        id: The CoinMarketCap currency ID of the base cryptocurrency or fiat to convert from. Example: "1" (optional)
        symbol: Alternatively the currency symbol of the base cryptocurrency or fiat to convert from. Example: "BTC". One "id" *or* "symbol" is required. Please note that starting in the v2 endpoint, due to the fact that a symbol is not unique, if you request by symbol each quote response will contain an array of objects containing all of the coins that use each requested symbol. The v1 endpoint will still return a single object, the highest ranked coin using that symbol. (optional)
        time: Optional timestamp (Unix or ISO 8601) to reference historical pricing during conversion. If not passed, the current time will be used. If passed, we'll reference the closest historic values available for this conversion. (optional)
        convert: Pass up to 120 comma-separated fiat or cryptocurrency symbols to convert the source amount to. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv2toolspriceconversion()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v2/tools/price-conversion"
        params = {
            "amount": amount,
            "id": id,
            "symbol": symbol,
            "time": time,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv2toolspriceconversion: {e}")
        return {"error": str(e), "endpoint": "/v2/tools/price-conversion"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="CMC Crypto Fear and Greed Historical"

)
async def getv3fearandgreedhistorical(
    context: Context,
    start: Optional[str] = None,
    limit: Optional[str] = None
) -> Dict[str, Any]:
    """
    CMC Crypto Fear and Greed Historical

    Generated from OpenAPI endpoint: GET /v3/fear-and-greed/historical

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv3fearandgreedhistorical()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
        params = {
            "start": start,
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv3fearandgreedhistorical: {e}")
        return {"error": str(e), "endpoint": "/v3/fear-and-greed/historical"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="CMC Crypto Fear and Greed Latest"

)
async def getv3fearandgreedlatest(
    context: Context
) -> Dict[str, Any]:
    """
    CMC Crypto Fear and Greed Latest

    Generated from OpenAPI endpoint: GET /v3/fear-and-greed/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)


    Returns:
        Dictionary with API response

    Example Usage:
        await getv3fearandgreedlatest()
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"
        params = {}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv3fearandgreedlatest: {e}")
        return {"error": str(e), "endpoint": "/v3/fear-and-greed/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Statistics Latest"

)
async def getv1blockchainstatisticslatest(
    context: Context,
    id: Optional[str] = None,
    symbol: Optional[str] = None,
    slug: Optional[str] = None
) -> Dict[str, Any]:
    """
    Statistics Latest

    Generated from OpenAPI endpoint: GET /v1/blockchain/statistics/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated cryptocurrency CoinMarketCap IDs to return blockchain data for. Pass `1,2,1027` to request all currently supported blockchains. (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Pass `BTC,LTC,ETH` to request all currently supported blockchains. (optional)
        slug: Alternatively pass a comma-separated list of cryptocurrency slugs. Pass `bitcoin,litecoin,ethereum` to request all currently supported blockchains. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1blockchainstatisticslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/blockchain/statistics/latest"
        params = {
            "id": id,
            "symbol": symbol,
            "slug": slug
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1blockchainstatisticslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/blockchain/statistics/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Community Trending Tokens"

)
async def getv1communitytrendingtoken(
    context: Context,
    limit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Community Trending Tokens

    Generated from OpenAPI endpoint: GET /v1/community/trending/token

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        limit: Optionally specify the number of results to return. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1communitytrendingtoken()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/community/trending/token"
        params = {
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1communitytrendingtoken: {e}")
        return {"error": str(e), "endpoint": "/v1/community/trending/token"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Community Trending Topics"

)
async def getv1communitytrendingtopic(
    context: Context,
    limit: Optional[str] = None
) -> Dict[str, Any]:
    """
    Community Trending Topics

    Generated from OpenAPI endpoint: GET /v1/community/trending/topic

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        limit: Optionally specify the number of results to return. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1communitytrendingtopic()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/community/trending/topic"
        params = {
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1communitytrendingtopic: {e}")
        return {"error": str(e), "endpoint": "/v1/community/trending/topic"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Content Post Comments"

)
async def getv1contentpostscomments(
    context: Context,
    post_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Content Post Comments

    Generated from OpenAPI endpoint: GET /v1/content/posts/comments

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        post_id: Required post ID. Example: 325670123 (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1contentpostscomments()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/content/posts/comments"
        params = {
            "post_id": post_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1contentpostscomments: {e}")
        return {"error": str(e), "endpoint": "/v1/content/posts/comments"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Historical v1 (deprecated)"

)
async def getv1cryptocurrencyquoteshistorical(
    context: Context,
    id: Optional[str] = None,
    symbol: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    count: Optional[str] = None,
    interval: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    aux: Optional[str] = None,
    skip_invalid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Historical v1 (deprecated)

    Generated from OpenAPI endpoint: GET /v1/cryptocurrency/quotes/historical

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated CoinMarketCap cryptocurrency IDs. Example: "1,2" (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". At least one "id" *or* "symbol" is required for this request. (optional)
        time_start: Timestamp (Unix or ISO 8601) to start returning quotes for. Optional, if not passed, we'll return quotes calculated in reverse from "time_end". (optional)
        time_end: Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive). Optional, if not passed, we'll default to the current time. If no "time_start" is passed, we return quotes in reverse order starting from this time. (optional)
        count: The number of interval periods to return results for. Optional, required if both "time_start" and "time_end" aren't supplied. The default is 10 items. The current query limit is 10000. (optional)
        interval: Interval of time to return data points for. See details in endpoint description. (optional)
        convert: By default market quotes are returned in USD. Optionally calculate market quotes in up to 3 other fiat currencies or cryptocurrencies. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `price,volume,market_cap,circulating_supply,total_supply,quote_timestamp,is_active,is_fiat,search_interval` to include all auxiliary fields. (optional)
        skip_invalid: Pass `true` to relax request validation rules. When requesting records on multiple cryptocurrencies an error is returned if no match is found for 1 or more requested cryptocurrencies. If set to true, invalid lookups will be skipped allowing valid cryptocurrencies to still be returned. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1cryptocurrencyquoteshistorical()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
        params = {
            "id": id,
            "symbol": symbol,
            "time_start": time_start,
            "time_end": time_end,
            "count": count,
            "interval": interval,
            "convert": convert,
            "convert_id": convert_id,
            "aux": aux,
            "skip_invalid": skip_invalid
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1cryptocurrencyquoteshistorical: {e}")
        return {"error": str(e), "endpoint": "/v1/cryptocurrency/quotes/historical"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Latest v1 (deprecated)"

)
async def getv1cryptocurrencyquoteslatest(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    symbol: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    aux: Optional[str] = None,
    skip_invalid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Latest v1 (deprecated)

    Generated from OpenAPI endpoint: GET /v1/cryptocurrency/quotes/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2 (optional)
        slug: Alternatively pass a comma-separated list of cryptocurrency slugs. Example: "bitcoin,ethereum" (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". At least one "id" *or* "slug" *or* "symbol" is required for this request. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply,market_cap_by_total_supply,volume_24h_reported,volume_7d,volume_7d_reported,volume_30d,volume_30d_reported,is_active,is_fiat` to include all auxiliary fields. (optional)
        skip_invalid: Pass `true` to relax request validation rules. When requesting records on multiple cryptocurrencies an error is returned if no match is found for 1 or more requested cryptocurrencies. If set to true, invalid lookups will be skipped allowing valid cryptocurrencies to still be returned. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1cryptocurrencyquoteslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        params = {
            "id": id,
            "slug": slug,
            "symbol": symbol,
            "convert": convert,
            "convert_id": convert_id,
            "aux": aux,
            "skip_invalid": skip_invalid
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1cryptocurrencyquoteslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/cryptocurrency/quotes/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Trending Gainers & Losers"

)
async def getv1cryptocurrencytrendinggainerslosers(
    context: Context,
    start: Optional[str] = None,
    limit: Optional[str] = None,
    time_period: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    sort: Optional[str] = None,
    sort_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trending Gainers & Losers

    Generated from OpenAPI endpoint: GET /v1/cryptocurrency/trending/gainers-losers

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)
        time_period: Adjusts the overall window of time for the biggest gainers and losers. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        sort: What field to sort the list of cryptocurrencies by. (optional)
        sort_dir: The direction in which to order cryptocurrencies against the specified sort. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1cryptocurrencytrendinggainerslosers()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/trending/gainers-losers"
        params = {
            "start": start,
            "limit": limit,
            "time_period": time_period,
            "convert": convert,
            "convert_id": convert_id,
            "sort": sort,
            "sort_dir": sort_dir
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1cryptocurrencytrendinggainerslosers: {e}")
        return {"error": str(e), "endpoint": "/v1/cryptocurrency/trending/gainers-losers"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Trending Latest"

)
async def getv1cryptocurrencytrendinglatest(
    context: Context,
    start: Optional[str] = None,
    limit: Optional[str] = None,
    time_period: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trending Latest

    Generated from OpenAPI endpoint: GET /v1/cryptocurrency/trending/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)
        time_period: Adjusts the overall window of time for the latest trending coins. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1cryptocurrencytrendinglatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/trending/latest"
        params = {
            "start": start,
            "limit": limit,
            "time_period": time_period,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1cryptocurrencytrendinglatest: {e}")
        return {"error": str(e), "endpoint": "/v1/cryptocurrency/trending/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Trending Most Visited"

)
async def getv1cryptocurrencytrendingmostvisited(
    context: Context,
    start: Optional[str] = None,
    limit: Optional[str] = None,
    time_period: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trending Most Visited

    Generated from OpenAPI endpoint: GET /v1/cryptocurrency/trending/most-visited

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)
        time_period: Adjusts the overall window of time for most visited currencies. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1cryptocurrencytrendingmostvisited()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/trending/most-visited"
        params = {
            "start": start,
            "limit": limit,
            "time_period": time_period,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1cryptocurrencytrendingmostvisited: {e}")
        return {"error": str(e), "endpoint": "/v1/cryptocurrency/trending/most-visited"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Listings Latest"

)
async def getv1exchangelistingslatest(
    context: Context,
    start: Optional[str] = None,
    limit: Optional[str] = None,
    sort: Optional[str] = None,
    sort_dir: Optional[str] = None,
    market_type: Optional[str] = None,
    category: Optional[str] = None,
    aux: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Listings Latest

    Generated from OpenAPI endpoint: GET /v1/exchange/listings/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)
        sort: What field to sort the list of exchanges by. (optional)
        sort_dir: The direction in which to order exchanges against the specified sort. (optional)
        market_type: The type of exchange markets to include in rankings. This field is deprecated. Please use "all" for accurate sorting. (optional)
        category: The category for this exchange. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `num_market_pairs,traffic_score,rank,exchange_score,effective_liquidity_24h,date_launched,fiats` to include all auxiliary fields. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1exchangelistingslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/exchange/listings/latest"
        params = {
            "start": start,
            "limit": limit,
            "sort": sort,
            "sort_dir": sort_dir,
            "market_type": market_type,
            "category": category,
            "aux": aux,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1exchangelistingslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/exchange/listings/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Market Pairs Latest"

)
async def getv1exchangemarketpairslatest(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    start: Optional[str] = None,
    limit: Optional[str] = None,
    aux: Optional[str] = None,
    matched_id: Optional[str] = None,
    matched_symbol: Optional[str] = None,
    category: Optional[str] = None,
    fee_type: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Market Pairs Latest

    Generated from OpenAPI endpoint: GET /v1/exchange/market-pairs/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: A CoinMarketCap exchange ID. Example: "1" (optional)
        slug: Alternatively pass an exchange "slug" (URL friendly all lowercase shorthand version of name with spaces replaced with hyphens). Example: "binance". One "id" *or* "slug" is required. (optional)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `num_market_pairs,category,fee_type,market_url,currency_name,currency_slug,price_quote,effective_liquidity,market_score,market_reputation` to include all auxiliary fields. (optional)
        matched_id: Optionally include one or more comma-delimited fiat or cryptocurrency IDs to filter market pairs by. For example `?matched_id=2781` would only return BTC markets that matched: "BTC/USD" or "USD/BTC" for the requested exchange. This parameter cannot be used when `matched_symbol` is used. (optional)
        matched_symbol: Optionally include one or more comma-delimited fiat or cryptocurrency symbols to filter market pairs by. For example `?matched_symbol=USD` would only return BTC markets that matched: "BTC/USD" or "USD/BTC" for the requested exchange. This parameter cannot be used when `matched_id` is used. (optional)
        category: The category of trading this market falls under. Spot markets are the most common but options include derivatives and OTC. (optional)
        fee_type: The fee type the exchange enforces for this market. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1exchangemarketpairslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/exchange/market-pairs/latest"
        params = {
            "id": id,
            "slug": slug,
            "start": start,
            "limit": limit,
            "aux": aux,
            "matched_id": matched_id,
            "matched_symbol": matched_symbol,
            "category": category,
            "fee_type": fee_type,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1exchangemarketpairslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/exchange/market-pairs/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Historical"

)
async def getv1exchangequoteshistorical(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    count: Optional[str] = None,
    interval: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Historical

    Generated from OpenAPI endpoint: GET /v1/exchange/quotes/historical

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated exchange CoinMarketCap ids. Example: "24,270" (optional)
        slug: Alternatively, one or more comma-separated exchange names in URL friendly shorthand "slug" format (all lowercase, spaces replaced with hyphens). Example: "binance,kraken". At least one "id" *or* "slug" is required. (optional)
        time_start: Timestamp (Unix or ISO 8601) to start returning quotes for. Optional, if not passed, we'll return quotes calculated in reverse from "time_end". (optional)
        time_end: Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive). Optional, if not passed, we'll default to the current time. If no "time_start" is passed, we return quotes in reverse order starting from this time. (optional)
        count: The number of interval periods to return results for. Optional, required if both "time_start" and "time_end" aren't supplied. The default is 10 items. The current query limit is 10000. (optional)
        interval: Interval of time to return data points for. See details in endpoint description. (optional)
        convert: By default market quotes are returned in USD. Optionally calculate market quotes in up to 3 other fiat currencies or cryptocurrencies. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1exchangequoteshistorical()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/exchange/quotes/historical"
        params = {
            "id": id,
            "slug": slug,
            "time_start": time_start,
            "time_end": time_end,
            "count": count,
            "interval": interval,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1exchangequoteshistorical: {e}")
        return {"error": str(e), "endpoint": "/v1/exchange/quotes/historical"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Latest"

)
async def getv1exchangequoteslatest(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    aux: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Latest

    Generated from OpenAPI endpoint: GET /v1/exchange/quotes/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated CoinMarketCap exchange IDs. Example: "1,2" (optional)
        slug: Alternatively, pass a comma-separated list of exchange "slugs" (URL friendly all lowercase shorthand version of name with spaces replaced with hyphens). Example: "binance,gdax". At least one "id" *or* "slug" is required. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `num_market_pairs,traffic_score,rank,exchange_score,liquidity_score,effective_liquidity_24h` to include all auxiliary fields. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1exchangequoteslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/exchange/quotes/latest"
        params = {
            "id": id,
            "slug": slug,
            "convert": convert,
            "convert_id": convert_id,
            "aux": aux
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1exchangequoteslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/exchange/quotes/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Historical"

)
async def getv1globalmetricsquoteshistorical(
    context: Context,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    count: Optional[str] = None,
    interval: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    aux: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Historical

    Generated from OpenAPI endpoint: GET /v1/global-metrics/quotes/historical

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        time_start: Timestamp (Unix or ISO 8601) to start returning quotes for. Optional, if not passed, we'll return quotes calculated in reverse from "time_end". (optional)
        time_end: Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive). Optional, if not passed, we'll default to the current time. If no "time_start" is passed, we return quotes in reverse order starting from this time. (optional)
        count: The number of interval periods to return results for. Optional, required if both "time_start" and "time_end" aren't supplied. The default is 10 items. The current query limit is 10000. (optional)
        interval: Interval of time to return data points for. See details in endpoint description. (optional)
        convert: By default market quotes are returned in USD. Optionally calculate market quotes in up to 3 other fiat currencies or cryptocurrencies. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `btc_dominance,eth_dominance,active_cryptocurrencies,active_exchanges,active_market_pairs,total_volume_24h,total_volume_24h_reported,altcoin_market_cap,altcoin_volume_24h,altcoin_volume_24h_reported,search_interval` to include all auxiliary fields. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1globalmetricsquoteshistorical()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/historical"
        params = {
            "time_start": time_start,
            "time_end": time_end,
            "count": count,
            "interval": interval,
            "convert": convert,
            "convert_id": convert_id,
            "aux": aux
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1globalmetricsquoteshistorical: {e}")
        return {"error": str(e), "endpoint": "/v1/global-metrics/quotes/historical"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Latest"

)
async def getv1globalmetricsquoteslatest(
    context: Context,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Latest

    Generated from OpenAPI endpoint: GET /v1/global-metrics/quotes/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1globalmetricsquoteslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        params = {
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1globalmetricsquoteslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/global-metrics/quotes/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Market Pairs Latest v2"

)
async def getv2cryptocurrencymarketpairslatest(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    symbol: Optional[str] = None,
    start: Optional[str] = None,
    limit: Optional[str] = None,
    sort_dir: Optional[str] = None,
    sort: Optional[str] = None,
    aux: Optional[str] = None,
    matched_id: Optional[str] = None,
    matched_symbol: Optional[str] = None,
    category: Optional[str] = None,
    fee_type: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Market Pairs Latest v2

    Generated from OpenAPI endpoint: GET /v2/cryptocurrency/market-pairs/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: A cryptocurrency or fiat currency by CoinMarketCap ID to list market pairs for. Example: "1" (optional)
        slug: Alternatively pass a cryptocurrency by slug. Example: "bitcoin" (optional)
        symbol: Alternatively pass a cryptocurrency by symbol. Fiat currencies are not supported by this field. Example: "BTC". A single cryptocurrency "id", "slug", *or* "symbol" is required. (optional)
        start: Optionally offset the start (1-based index) of the paginated list of items to return. (optional)
        limit: Optionally specify the number of results to return. Use this parameter and the "start" parameter to determine your own pagination size. (optional)
        sort_dir: Optionally specify the sort direction of markets returned. (optional)
        sort: Optionally specify the sort order of markets returned. By default we return a strict sort on 24 hour reported volume. Pass `cmc_rank` to return a CMC methodology based sort where markets with excluded volumes are returned last. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `num_market_pairs,category,fee_type,market_url,currency_name,currency_slug,price_quote,notice,cmc_rank,effective_liquidity,market_score,market_reputation` to include all auxiliary fields. (optional)
        matched_id: Optionally include one or more fiat or cryptocurrency IDs to filter market pairs by. For example `?id=1&matched_id=2781` would only return BTC markets that matched: "BTC/USD" or "USD/BTC". This parameter cannot be used when `matched_symbol` is used. (optional)
        matched_symbol: Optionally include one or more fiat or cryptocurrency symbols to filter market pairs by. For example `?symbol=BTC&matched_symbol=USD` would only return BTC markets that matched: "BTC/USD" or "USD/BTC". This parameter cannot be used when `matched_id` is used. (optional)
        category: The category of trading this market falls under. Spot markets are the most common but options include derivatives and OTC. (optional)
        fee_type: The fee type the exchange enforces for this market. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv2cryptocurrencymarketpairslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/market-pairs/latest"
        params = {
            "id": id,
            "slug": slug,
            "symbol": symbol,
            "start": start,
            "limit": limit,
            "sort_dir": sort_dir,
            "sort": sort,
            "aux": aux,
            "matched_id": matched_id,
            "matched_symbol": matched_symbol,
            "category": category,
            "fee_type": fee_type,
            "convert": convert,
            "convert_id": convert_id
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv2cryptocurrencymarketpairslatest: {e}")
        return {"error": str(e), "endpoint": "/v2/cryptocurrency/market-pairs/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="OHLCV Historical v2"

)
async def getv2cryptocurrencyohlcvhistorical(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    symbol: Optional[str] = None,
    time_period: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    count: Optional[str] = None,
    interval: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    skip_invalid: Optional[str] = None
) -> Dict[str, Any]:
    """
    OHLCV Historical v2

    Generated from OpenAPI endpoint: GET /v2/cryptocurrency/ohlcv/historical

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated CoinMarketCap cryptocurrency IDs. Example: "1,1027" (optional)
        slug: Alternatively pass a comma-separated list of cryptocurrency slugs. Example: "bitcoin,ethereum" (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". At least one "id" *or* "slug" *or* "symbol" is required for this request. (optional)
        time_period: Time period to return OHLCV data for. The default is "daily". If hourly, the open will be 01:00 and the close will be 01:59. If daily, the open will be 00:00:00 for the day and close will be 23:59:99 for the same day. See the main endpoint description for details. (optional)
        time_start: Timestamp (Unix or ISO 8601) to start returning OHLCV time periods for. Only the date portion of the timestamp is used for daily OHLCV so it's recommended to send an ISO date format like "2018-09-19" without time. (optional)
        time_end: Timestamp (Unix or ISO 8601) to stop returning OHLCV time periods for (inclusive). Optional, if not passed we'll default to the current time. Only the date portion of the timestamp is used for daily OHLCV so it's recommended to send an ISO date format like "2018-09-19" without time. (optional)
        count: Optionally limit the number of time periods to return results for. The default is 10 items. The current query limit is 10000 items. (optional)
        interval: Optionally adjust the interval that "time_period" is sampled. For example with interval=monthly&time_period=daily you will see a daily OHLCV record for January, February, March and so on. See main endpoint description for available options. (optional)
        convert: By default market quotes are returned in USD. Optionally calculate market quotes in up to 3 fiat currencies or cryptocurrencies. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        skip_invalid: Pass `true` to relax request validation rules. When requesting records on multiple cryptocurrencies an error is returned if any invalid cryptocurrencies are requested or a cryptocurrency does not have matching records in the requested timeframe. If set to true, invalid lookups will be skipped allowing valid cryptocurrencies to still be returned. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv2cryptocurrencyohlcvhistorical()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/ohlcv/historical"
        params = {
            "id": id,
            "slug": slug,
            "symbol": symbol,
            "time_period": time_period,
            "time_start": time_start,
            "time_end": time_end,
            "count": count,
            "interval": interval,
            "convert": convert,
            "convert_id": convert_id,
            "skip_invalid": skip_invalid
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv2cryptocurrencyohlcvhistorical: {e}")
        return {"error": str(e), "endpoint": "/v2/cryptocurrency/ohlcv/historical"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="OHLCV Latest v2"

)
async def getv2cryptocurrencyohlcvlatest(
    context: Context,
    id: Optional[str] = None,
    symbol: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    skip_invalid: Optional[str] = None
) -> Dict[str, Any]:
    """
    OHLCV Latest v2

    Generated from OpenAPI endpoint: GET /v2/cryptocurrency/ohlcv/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2 (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". At least one "id" *or* "symbol" is required. (optional)
        convert: Optionally calculate market quotes in up to 120 currencies at once by passing a comma-separated list of cryptocurrency or fiat currency symbols. Each additional convert option beyond the first requires an additional call credit. A list of supported fiat options can be found [here](#section/Standards-and-Conventions). Each conversion is returned in its own "quote" object. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        skip_invalid: Pass `true` to relax request validation rules. When requesting records on multiple cryptocurrencies an error is returned if any invalid cryptocurrencies are requested or a cryptocurrency does not have matching records in the requested timeframe. If set to true, invalid lookups will be skipped allowing valid cryptocurrencies to still be returned. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv2cryptocurrencyohlcvlatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/ohlcv/latest"
        params = {
            "id": id,
            "symbol": symbol,
            "convert": convert,
            "convert_id": convert_id,
            "skip_invalid": skip_invalid
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv2cryptocurrencyohlcvlatest: {e}")
        return {"error": str(e), "endpoint": "/v2/cryptocurrency/ohlcv/latest"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Quotes Historical v2"

)
async def getv2cryptocurrencyquoteshistorical(
    context: Context,
    id: Optional[str] = None,
    symbol: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    count: Optional[str] = None,
    interval: Optional[str] = None,
    convert: Optional[str] = None,
    convert_id: Optional[str] = None,
    aux: Optional[str] = None,
    skip_invalid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quotes Historical v2

    Generated from OpenAPI endpoint: GET /v2/cryptocurrency/quotes/historical

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated CoinMarketCap cryptocurrency IDs. Example: "1,2" (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". At least one "id" *or* "symbol" is required for this request. (optional)
        time_start: Timestamp (Unix or ISO 8601) to start returning quotes for. Optional, if not passed, we'll return quotes calculated in reverse from "time_end". (optional)
        time_end: Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive). Optional, if not passed, we'll default to the current time. If no "time_start" is passed, we return quotes in reverse order starting from this time. (optional)
        count: The number of interval periods to return results for. Optional, required if both "time_start" and "time_end" aren't supplied. The default is 10 items. The current query limit is 10000. (optional)
        interval: Interval of time to return data points for. See details in endpoint description. (optional)
        convert: By default market quotes are returned in USD. Optionally calculate market quotes in up to 3 other fiat currencies or cryptocurrencies. (optional)
        convert_id: Optionally calculate market quotes by CoinMarketCap ID instead of symbol. This option is identical to `convert` outside of ID format. Ex: convert_id=1,2781 would replace convert=BTC,USD in your query. This parameter cannot be used when `convert` is used. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `price,volume,market_cap,circulating_supply,total_supply,quote_timestamp,is_active,is_fiat,search_interval` to include all auxiliary fields. (optional)
        skip_invalid: Pass `true` to relax request validation rules. When requesting records on multiple cryptocurrencies an error is returned if no match is found for 1 or more requested cryptocurrencies. If set to true, invalid lookups will be skipped allowing valid cryptocurrencies to still be returned. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv2cryptocurrencyquoteshistorical()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/historical"
        params = {
            "id": id,
            "symbol": symbol,
            "time_start": time_start,
            "time_end": time_end,
            "count": count,
            "interval": interval,
            "convert": convert,
            "convert_id": convert_id,
            "aux": aux,
            "skip_invalid": skip_invalid
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv2cryptocurrencyquoteshistorical: {e}")
        return {"error": str(e), "endpoint": "/v2/cryptocurrency/quotes/historical"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="5000",  # 0.005 tokens
        asset=TokenAsset(
            address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            decimals=6,
            network="sepolia",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="FCAS Quotes Latest (deprecated)"

)
async def getv1partnersflipsidecryptofcasquoteslatest(
    context: Context,
    id: Optional[str] = None,
    slug: Optional[str] = None,
    symbol: Optional[str] = None,
    aux: Optional[str] = None
) -> Dict[str, Any]:
    """
    FCAS Quotes Latest (deprecated)

    Generated from OpenAPI endpoint: GET /v1/partners/flipside-crypto/fcas/quotes/latest

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        id: One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2 (optional)
        slug: Alternatively pass a comma-separated list of cryptocurrency slugs. Example: "bitcoin,ethereum" (optional)
        symbol: Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". At least one "id" *or* "slug" *or* "symbol" is required for this request. (optional)
        aux: Optionally specify a comma-separated list of supplemental data fields to return. Pass `point_change_24h,percent_change_24h` to include all auxiliary fields. (optional)

    Returns:
        Dictionary with API response

    Example Usage:
        await getv1partnersflipsidecryptofcasquoteslatest()

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://pro-api.coinmarketcap.com/v1/partners/flipside-crypto/fcas/quotes/latest"
        params = {
            "id": id,
            "slug": slug,
            "symbol": symbol,
            "aux": aux
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in getv1partnersflipsidecryptofcasquoteslatest: {e}")
        return {"error": str(e), "endpoint": "/v1/partners/flipside-crypto/fcas/quotes/latest"}


# TODO: Add your API-specific functions here

# ============================================================================
# APPLICATION SETUP WITH STARLETTE MIDDLEWARE
# ============================================================================

def create_app_with_middleware():
    """
    Create Starlette app with d402 payment middleware.
    
    Strategy:
    1. Get FastMCP's Starlette app via streamable_http_app()
    2. Extract payment configs from @require_payment_for_tool decorators
    3. Add Starlette middleware with extracted configs
    4. Single source of truth - no duplication!
    """
    logger.info("🔧 Creating FastMCP app with middleware...")
    
    # Get FastMCP's Starlette app
    app = mcp.streamable_http_app()
    logger.info(f"✅ Got FastMCP Starlette app")
    
    # Extract payment configs from decorators (single source of truth!)
    tool_payment_configs = extract_payment_configs_from_mcp(mcp, SERVER_ADDRESS)
    logger.info(f"📊 Extracted {len(tool_payment_configs)} payment configs from @require_payment_for_tool decorators")
    
    # D402 Configuration
    facilitator_url = os.getenv("FACILITATOR_URL") or os.getenv("D402_FACILITATOR_URL")
    operator_key = os.getenv("MCP_OPERATOR_PRIVATE_KEY")
    network = os.getenv("NETWORK", "sepolia")
    testing_mode = os.getenv("D402_TESTING_MODE", "false").lower() == "true"
    
    # Log D402 configuration with prominent facilitator info
    logger.info("="*60)
    logger.info("D402 Payment Protocol Configuration:")
    logger.info(f"  Server Address: {SERVER_ADDRESS}")
    logger.info(f"  Network: {network}")
    logger.info(f"  Operator Key: {'✅ Set' if operator_key else '❌ Not set'}")
    logger.info(f"  Testing Mode: {'⚠️  ENABLED (bypasses facilitator)' if testing_mode else '✅ DISABLED (uses facilitator)'}")
    logger.info("="*60)
    
    if not facilitator_url and not testing_mode:
        logger.error("❌ FACILITATOR_URL required when testing_mode is disabled!")
        raise ValueError("Set FACILITATOR_URL or enable D402_TESTING_MODE=true")
    
    if facilitator_url:
        logger.info(f"🌐 FACILITATOR: {facilitator_url}")
        if "localhost" in facilitator_url or "127.0.0.1" in facilitator_url or "host.docker.internal" in facilitator_url:
            logger.info(f"   📍 Using LOCAL facilitator for development")
        else:
            logger.info(f"   🌍 Using REMOTE facilitator for production")
    else:
        logger.warning("⚠️  D402 Testing Mode - Facilitator bypassed")
    logger.info("="*60)
    
    # Add CORS middleware first (processes before other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["mcp-session-id"],  # Expose custom headers to browser
    )
    logger.info("✅ Added CORS middleware (allow all origins, expose mcp-session-id)")
    
    # Add D402 payment middleware with extracted configs
    app.add_middleware(
        D402PaymentMiddleware,
        tool_payment_configs=tool_payment_configs,
        server_address=SERVER_ADDRESS,
        requires_auth=True,  # Extracts API keys + checks payment
        internal_api_key=API_KEY,  # Server's internal key (for Mode 2: paid access)
        testing_mode=testing_mode,
        facilitator_url=facilitator_url,
        facilitator_api_key=os.getenv("D402_FACILITATOR_API_KEY"),
        server_name="nikola-test-coinmarketcap-mcp-server"  # MCP server ID for tracking
    )
    logger.info("✅ Added D402PaymentMiddleware")
    logger.info("   - Auth extraction: Enabled")
    logger.info("   - Dual mode: API key OR payment")
    
    # Add health check endpoint (bypasses middleware)
    @app.route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        """Health check endpoint for container orchestration."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "nikola-test-coinmarketcap-mcp-server",
                "timestamp": datetime.now().isoformat()
            }
        )
    logger.info("✅ Added /health endpoint")
    
    return app

if __name__ == "__main__":
    logger.info("="*80)
    logger.info(f"Starting Nikola Test CoinMarketCap MCP Server")
    logger.info("="*80)
    logger.info("Architecture:")
    logger.info("  1. D402PaymentMiddleware intercepts requests")
    logger.info("     - Extracts API keys from Authorization header")
    logger.info("     - Checks payment → HTTP 402 if no API key AND no payment")
    logger.info("  2. FastMCP processes valid requests with tool decorators")
    logger.info("="*80)
    
    # Create app with middleware
    app = create_app_with_middleware()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
