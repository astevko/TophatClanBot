"""
Roblox API integration for TophatC Clan Bot
Handles Roblox group rank verification and updates.
"""

import logging
from typing import Any, Dict, Optional

import aiohttp

from config import Config

# Import appropriate database module based on configuration
if Config.USE_ORACLE:
    import database_oracle as database
elif Config.USE_SQLITE:
    import database
else:
    import database_postgres as database

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
                json={"usernames": [username], "excludeBannedUsers": True},
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
            async with session.get(f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles") as response:
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
            async with session.get(f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles") as response:
                if response.status == 200:
                    data = await response.json()
                    for group in data.get("data", []):
                        if group.get("group", {}).get("id") == Config.ROBLOX_GROUP_ID:
                            return {
                                "rank_id": group["role"]["id"],
                                "rank_name": group["role"]["name"],
                                "rank": group["role"]["rank"],
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
    
    The new_rank_id parameter can be either:
    - A Roblox role ID (large number, e.g., 50689939)
    - A Roblox rank number (0-255, e.g., 47)
    
    If a rank number is provided, it will be automatically converted to the role ID.

    Note: This requires the bot to have proper permissions in the Roblox group
    and valid authentication credentials (API key or cookie).
    """
    try:
        # Check if new_rank_id is a rank number (0-255) or a role ID
        # Rank numbers are small, role IDs are large numbers
        actual_role_id = new_rank_id
        
        # If it's a small number (likely a rank number), try to convert it
        if new_rank_id <= 255:
            converted_role_id = await get_role_id_from_rank_number(new_rank_id)
            if converted_role_id:
                actual_role_id = converted_role_id
                logger.info(
                    f"Converted rank number {new_rank_id} to role ID {actual_role_id} for {username}"
                )
            else:
                # It might still be a valid role ID that happens to be small
                # Let validation check if it exists
                pass
        
        # Validate that the role exists before attempting to update
        roles = await get_group_roles()
        if roles is None:
            logger.error(f"Could not fetch group roles to validate rank update for {username}")
            return False
        
        role_ids = [role["id"] for role in roles]
        if actual_role_id not in role_ids:
            logger.error(
                f"Cannot update rank for {username}: "
                f"Role ID {actual_role_id} (from input {new_rank_id}) does not exist in the Roblox group. "
                f"Available role IDs: {role_ids}"
            )
            return False
        
        user_id = await get_user_id_from_username(username)
        if not user_id:
            logger.error(f"Could not find user ID for {username}")
            return False

        # Prepare headers based on available authentication
        headers = {"Content-Type": "application/json"}

        # Use Open Cloud API if API key is available
        if Config.ROBLOX_API_KEY:
            headers["x-api-key"] = Config.ROBLOX_API_KEY

            # Open Cloud API endpoint
            # Note: Open Cloud API expects full resource path for role
            async with aiohttp.ClientSession() as session:
                url = f"{ROBLOX_API_BASE}/cloud/v2/groups/{Config.ROBLOX_GROUP_ID}/memberships/{user_id}"

                # Roblox Open Cloud API expects role as a full resource path
                role_path = f"groups/{Config.ROBLOX_GROUP_ID}/roles/{actual_role_id}"

                async with session.patch(
                    url, headers=headers, json={"role": role_path}
                ) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Successfully updated rank for {username} to role ID {actual_role_id} (from input {new_rank_id})")
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
                    headers=headers,
                ) as token_response:
                    csrf_token = token_response.headers.get("x-csrf-token")
                    if csrf_token:
                        headers["x-csrf-token"] = csrf_token

                # Update the rank
                url = f"{ROBLOX_GROUPS_API}/groups/{Config.ROBLOX_GROUP_ID}/users/{user_id}"
                async with session.patch(
                    url, headers=headers, json={"roleId": actual_role_id}
                ) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Successfully updated rank for {username} to role ID {actual_role_id} (from input {new_rank_id})")
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
                        "member_count": data.get("memberCount"),
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
                        roles.append(
                            {
                                "id": role["id"],
                                "name": role["name"],
                                "rank": role["rank"],
                                "member_count": role.get("memberCount", 0),
                            }
                        )
                    return roles
                else:
                    logger.error(f"Failed to get group roles: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error getting group roles: {e}")
        return None


async def get_role_id_from_rank_number(rank_number: int) -> Optional[int]:
    """
    Convert a Roblox rank number (0-255) to the corresponding role ID.
    
    Args:
        rank_number: The rank number (0-255)
        
    Returns:
        The role ID if found, None otherwise
    """
    try:
        roles = await get_group_roles()
        if roles is None:
            return None
        
        # Find the role with matching rank number
        for role in roles:
            if role["rank"] == rank_number:
                return role["id"]
        
        return None
    except Exception as e:
        logger.error(f"Error converting rank number {rank_number} to role ID: {e}")
        return None


async def validate_role_exists(role_id: int) -> bool:
    """
    Validate that a role ID exists in the Roblox group.
    Also checks if the provided value is a rank number (0-255) and converts it.
    
    Args:
        role_id: The role ID to validate, or a rank number (0-255)
        
    Returns:
        True if the role exists, False if it doesn't exist or can't be validated
    """
    try:
        roles = await get_group_roles()
        if roles is None:
            logger.warning(f"Could not fetch group roles to validate role ID {role_id}")
            return False
        
        # Check if the role ID exists in the list of roles
        role_ids = [role["id"] for role in roles]
        if role_id in role_ids:
            return True
        
        # If not found as a role ID, check if it's a rank number (0-255)
        # Rank numbers are typically small (0-255), while role IDs are large numbers
        if role_id <= 255:
            rank_numbers = [role["rank"] for role in roles]
            if role_id in rank_numbers:
                # It's a valid rank number, but we need the actual role ID
                logger.warning(
                    f"Provided value {role_id} is a rank number, not a role ID. "
                    f"Use get_role_id_from_rank_number() to convert it first."
                )
                return False
        
        logger.error(
            f"Role ID {role_id} does not exist in the group. "
            f"Available role IDs: {role_ids}"
        )
        return False
    except Exception as e:
        logger.error(f"Error validating role ID {role_id}: {e}")
        return False


async def test_roblox_connection() -> Dict[str, Any]:
    """Test the Roblox API connection and permissions."""
    results = {
        "group_info": False,
        "group_roles": False,
        "authentication_configured": False,
        "api_key_valid": False,
        "api_key_test_status": None,
        "api_key_error": None,
        "auth_method": None,
        "errors": [],
    }

    # Test getting group info (doesn't require auth)
    group_info = await get_group_info()
    if group_info:
        results["group_info"] = True
        results["group_name"] = group_info.get("name", "Unknown")
        results["group_id"] = group_info.get("id")
        logger.info(f"Successfully connected to group: {group_info['name']}")
    else:
        results["errors"].append("Failed to get group info - check ROBLOX_GROUP_ID")

    # Test getting group roles (doesn't require auth)
    roles = await get_group_roles()
    if roles:
        results["group_roles"] = True
        results["role_count"] = len(roles)
        logger.info(f"Successfully retrieved {len(roles)} group roles")
    else:
        results["errors"].append("Failed to get group roles")

    # Check if authentication credentials are configured
    if Config.ROBLOX_API_KEY:
        results["authentication_configured"] = True
        results["auth_method"] = "API Key"
        
        # Test if API key is actually valid by making an authenticated request
        # We'll try to access a protected endpoint (getting group memberships requires auth)
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": Config.ROBLOX_API_KEY,
                }
                # Test with getting group info via authenticated endpoint (Open Cloud API)
                # This endpoint will return 401 if the API key is invalid
                url = f"{ROBLOX_API_BASE}/cloud/v2/groups/{Config.ROBLOX_GROUP_ID}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        results["api_key_valid"] = True
                        results["api_key_test_status"] = "valid"
                        logger.info("✅ API key is valid and authenticated successfully")
                    elif response.status == 401:
                        results["api_key_valid"] = False
                        results["api_key_test_status"] = "invalid"
                        error_data = await response.text()
                        results["api_key_error"] = f"401 Unauthorized - Invalid API key"
                        results["errors"].append("API key authentication failed (401 Unauthorized)")
                        logger.error(f"❌ API key is invalid: {error_data}")
                    elif response.status == 403:
                        results["api_key_valid"] = False
                        results["api_key_test_status"] = "forbidden"
                        error_data = await response.text()
                        results["api_key_error"] = f"403 Forbidden - API key lacks permissions"
                        results["errors"].append("API key lacks required permissions (403 Forbidden)")
                        logger.error(f"⚠️ API key lacks permissions: {error_data}")
                    else:
                        results["api_key_valid"] = False
                        results["api_key_test_status"] = f"error_{response.status}"
                        error_data = await response.text()
                        results["api_key_error"] = f"HTTP {response.status}: {error_data[:200]}"
                        results["errors"].append(f"API key test returned status {response.status}")
                        logger.warning(f"API key test returned status {response.status}: {error_data[:200]}")
        except Exception as e:
            results["api_key_valid"] = False
            results["api_key_test_status"] = "exception"
            results["api_key_error"] = str(e)
            results["errors"].append(f"Exception testing API key: {str(e)}")
            logger.error(f"Exception testing API key: {e}")
            
    elif Config.ROBLOX_COOKIE:
        results["authentication_configured"] = True
        results["auth_method"] = "Cookie"
        results["api_key_test_status"] = "cookie_auth"
        logger.info("Cookie authentication configured (API key test not applicable)")
    else:
        results["errors"].append("No authentication credentials configured (ROBLOX_API_KEY or ROBLOX_COOKIE)")

    return results


async def verify_roblox_credentials() -> bool:
    """
    Verify that Roblox credentials are valid and have proper permissions.
    This should be called during bot startup.
    """
    try:
        # Test basic API access
        group_info = await get_group_info()
        if not group_info:
            logger.error("Failed to retrieve group info - check ROBLOX_GROUP_ID")
            return False

        logger.info(f"✅ Connected to Roblox group: {group_info['name']}")

        # Test group roles access
        roles = await get_group_roles()
        if not roles:
            logger.error("Failed to retrieve group roles")
            return False

        logger.info(f"✅ Retrieved {len(roles)} group roles")

        # Check if credentials are configured
        if not Config.ROBLOX_API_KEY and not Config.ROBLOX_COOKIE:
            logger.warning(
                "⚠️ No Roblox authentication credentials configured - rank updates will not work"
            )
            return False

        logger.info("✅ Roblox authentication credentials configured")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to verify Roblox credentials: {e}")
        return False


async def get_database_rank_by_roblox_id(roblox_rank_id: int, roblox_rank_number: int = None):
    """
    Get the database rank that corresponds to a Roblox group rank ID.
    Falls back to matching by rank number if ID doesn't match.
    """
    ranks = await database.get_all_ranks()

    # First try: Match by exact Roblox rank ID
    for rank in ranks:
        if rank["roblox_group_rank_id"] == roblox_rank_id:
            return rank

    # Second try: Match by rank number (if provided)
    # This handles cases where the database uses rank numbers instead of role IDs
    if roblox_rank_number is not None:
        for rank in ranks:
            if rank["roblox_group_rank_id"] == roblox_rank_number:
                return rank

    # No match found
    logger.warning(
        f"No database rank found for Roblox rank ID {roblox_rank_id} (rank number: {roblox_rank_number})"
    )
    return None


async def compare_ranks(discord_member_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Compare a member's Discord rank with their Roblox rank.
    Returns a dict with comparison results if there's a mismatch, None if in sync.
    """
    try:
        # Get their current Roblox rank
        roblox_rank = await get_member_rank(discord_member_data["roblox_username"])
        if not roblox_rank:
            return {
                "status": "error",
                "message": f"Could not fetch Roblox rank for {discord_member_data['roblox_username']}",
            }

        # Get the Discord rank info
        discord_rank = await database.get_rank_by_order(discord_member_data["current_rank"])
        if not discord_rank:
            return {"status": "error", "message": "Could not find Discord rank in database"}

        # Find the corresponding database rank for the Roblox rank
        # Try matching by both rank_id and rank number
        target_rank = await get_database_rank_by_roblox_id(
            roblox_rank["rank_id"], roblox_rank["rank"]
        )

        # Check if ranks match (by rank_id OR rank number)
        if (
            discord_rank["roblox_group_rank_id"] == roblox_rank["rank_id"]
            or discord_rank["roblox_group_rank_id"] == roblox_rank["rank"]
        ):
            return None  # Ranks are in sync

        return {
            "status": "mismatch",
            "discord_rank": discord_rank,
            "roblox_rank": roblox_rank,
            "target_rank": target_rank,
            "member_data": discord_member_data,
        }

    except Exception as e:
        logger.error(
            f"Error comparing ranks for {discord_member_data.get('roblox_username', 'unknown')}: {e}"
        )
        return {"status": "error", "message": str(e)}


async def sync_member_rank_from_roblox(discord_id: int) -> Dict[str, Any]:
    """
    Sync a member's Discord rank with their current Roblox rank.
    Returns a dict with the sync results.
    """
    try:
        # Get member from database
        member = await database.get_member(discord_id)
        if not member:
            return {"success": False, "error": "Member not found in database"}

        # Compare ranks
        comparison = await compare_ranks(member)

        if comparison is None:
            # Already in sync
            return {"success": True, "action": "none", "message": "Ranks already in sync"}

        if comparison["status"] == "error":
            return {"success": False, "error": comparison["message"]}

        # Ranks don't match - update Discord rank
        target_rank = comparison["target_rank"]
        if not target_rank:
            # No matching rank found - log and skip instead of erroring
            logger.warning(
                f"Cannot sync {member['roblox_username']}: "
                f"No database rank matches Roblox rank '{comparison['roblox_rank']['rank_name']}' "
                f"(ID: {comparison['roblox_rank']['rank_id']}, Rank: {comparison['roblox_rank']['rank']})"
            )
            return {
                "success": True,
                "action": "skipped",
                "reason": f"No database rank matches Roblox rank '{comparison['roblox_rank']['rank_name']}'",
                "roblox_rank": comparison["roblox_rank"],
            }

        # Update the rank in database
        await database.set_member_rank(discord_id, target_rank["rank_order"])

        return {
            "success": True,
            "action": "updated",
            "old_rank": comparison["discord_rank"],
            "new_rank": target_rank,
            "roblox_rank": comparison["roblox_rank"],
        }

    except Exception as e:
        logger.error(f"Error syncing member rank: {e}")
        return {"success": False, "error": str(e)}
