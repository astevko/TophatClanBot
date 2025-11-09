"""
Roblox API integration for TophatC Clan Bot
Handles Roblox group rank verification and updates.
"""

import aiohttp
import logging
from typing import Optional, Dict, Any

from config import Config

logger = logging.getLogger(__name__)

# Roblox API endpoints
ROBLOX_API_BASE = "https://apis.roblox.com"
ROBLOX_GROUPS_API = "https://groups.roblox.com/v1"
ROBLOX_USERS_API = "https://users.roblox.com/v1"


async def get_user_id_from_username(username: str) -> Optional[int]:
    """Get Roblox user ID from username."""
    try:
        async with aiohttp.ClientSession() as session:
            # Use the user search API
            async with session.post(
                f"{ROBLOX_USERS_API}/usernames/users",
                json={"usernames": [username], "excludeBannedUsers": True}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        return data["data"][0]["id"]
                else:
                    logger.error(f"Failed to get user ID for {username}: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error getting user ID for {username}: {e}")
        return None


async def verify_group_membership(username: str) -> bool:
    """Verify if a user is a member of the configured Roblox group."""
    try:
        user_id = await get_user_id_from_username(username)
        if not user_id:
            return False
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    for group in data.get("data", []):
                        if group.get("group", {}).get("id") == Config.ROBLOX_GROUP_ID:
                            return True
                    return False
                else:
                    logger.error(f"Failed to verify group membership: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Error verifying group membership for {username}: {e}")
        return False


async def get_member_rank(username: str) -> Optional[Dict[str, Any]]:
    """Get a member's current rank in the Roblox group."""
    try:
        user_id = await get_user_id_from_username(username)
        if not user_id:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    for group in data.get("data", []):
                        if group.get("group", {}).get("id") == Config.ROBLOX_GROUP_ID:
                            return {
                                "rank_id": group["role"]["id"],
                                "rank_name": group["role"]["name"],
                                "rank": group["role"]["rank"]
                            }
                    return None
                else:
                    logger.error(f"Failed to get member rank: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error getting member rank for {username}: {e}")
        return None


async def update_member_rank(username: str, new_rank_id: int) -> bool:
    """
    Update a member's rank in the Roblox group.
    
    Note: This requires the bot to have proper permissions in the Roblox group
    and valid authentication credentials (API key or cookie).
    """
    try:
        user_id = await get_user_id_from_username(username)
        if not user_id:
            logger.error(f"Could not find user ID for {username}")
            return False
        
        # Prepare headers based on available authentication
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use Open Cloud API if API key is available
        if Config.ROBLOX_API_KEY:
            headers["x-api-key"] = Config.ROBLOX_API_KEY
            
            # Open Cloud API endpoint
            async with aiohttp.ClientSession() as session:
                url = f"{ROBLOX_API_BASE}/cloud/v2/groups/{Config.ROBLOX_GROUP_ID}/memberships/{user_id}"
                async with session.patch(
                    url,
                    headers=headers,
                    json={"role": str(new_rank_id)}
                ) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Successfully updated rank for {username} to {new_rank_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update rank: {response.status} - {error_text}")
                        return False
        
        # Fallback to cookie-based authentication (legacy method)
        elif Config.ROBLOX_COOKIE:
            headers[".ROBLOSECURITY"] = Config.ROBLOX_COOKIE
            
            async with aiohttp.ClientSession() as session:
                # First, get CSRF token
                async with session.post(
                    f"{ROBLOX_GROUPS_API}/groups/{Config.ROBLOX_GROUP_ID}/users/{user_id}",
                    headers=headers
                ) as token_response:
                    csrf_token = token_response.headers.get("x-csrf-token")
                    if csrf_token:
                        headers["x-csrf-token"] = csrf_token
                
                # Update the rank
                url = f"{ROBLOX_GROUPS_API}/groups/{Config.ROBLOX_GROUP_ID}/users/{user_id}"
                async with session.patch(
                    url,
                    headers=headers,
                    json={"roleId": new_rank_id}
                ) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Successfully updated rank for {username} to {new_rank_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update rank: {response.status} - {error_text}")
                        return False
        else:
            logger.error("No Roblox authentication credentials configured")
            return False
    
    except Exception as e:
        logger.error(f"Error updating member rank for {username}: {e}")
        return False


async def get_group_info() -> Optional[Dict[str, Any]]:
    """Get information about the configured Roblox group."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ROBLOX_GROUPS_API}/groups/{Config.ROBLOX_GROUP_ID}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "owner": data.get("owner", {}).get("username"),
                        "member_count": data.get("memberCount")
                    }
                else:
                    logger.error(f"Failed to get group info: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error getting group info: {e}")
        return None


async def get_group_roles() -> Optional[list]:
    """Get all available roles in the Roblox group."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ROBLOX_GROUPS_API}/groups/{Config.ROBLOX_GROUP_ID}/roles"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    roles = []
                    for role in data.get("roles", []):
                        roles.append({
                            "id": role["id"],
                            "name": role["name"],
                            "rank": role["rank"],
                            "member_count": role.get("memberCount", 0)
                        })
                    return roles
                else:
                    logger.error(f"Failed to get group roles: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error getting group roles: {e}")
        return None


async def test_roblox_connection() -> Dict[str, Any]:
    """Test the Roblox API connection and permissions."""
    results = {
        "group_info": False,
        "group_roles": False,
        "authentication": False,
        "errors": []
    }
    
    # Test getting group info
    group_info = await get_group_info()
    if group_info:
        results["group_info"] = True
        logger.info(f"Successfully connected to group: {group_info['name']}")
    else:
        results["errors"].append("Failed to get group info")
    
    # Test getting group roles
    roles = await get_group_roles()
    if roles:
        results["group_roles"] = True
        logger.info(f"Successfully retrieved {len(roles)} group roles")
    else:
        results["errors"].append("Failed to get group roles")
    
    # Test authentication (check if credentials are configured)
    if Config.ROBLOX_API_KEY or Config.ROBLOX_COOKIE:
        results["authentication"] = True
        logger.info("Authentication credentials configured")
    else:
        results["errors"].append("No authentication credentials configured")
    
    return results

