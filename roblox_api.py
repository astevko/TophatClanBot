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

    Note: This requires the bot to have proper permissions in the Roblox group
    and valid authentication credentials (API key or cookie).
    """
    try:
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
                role_path = f"groups/{Config.ROBLOX_GROUP_ID}/roles/{new_rank_id}"

                async with session.patch(
                    url, headers=headers, json={"role": role_path}
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
                    headers=headers,
                ) as token_response:
                    csrf_token = token_response.headers.get("x-csrf-token")
                    if csrf_token:
                        headers["x-csrf-token"] = csrf_token

                # Update the rank
                url = f"{ROBLOX_GROUPS_API}/groups/{Config.ROBLOX_GROUP_ID}/users/{user_id}"
                async with session.patch(
                    url, headers=headers, json={"roleId": new_rank_id}
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


async def test_roblox_connection() -> Dict[str, Any]:
    """Test the Roblox API connection and permissions."""
    results = {"group_info": False, "group_roles": False, "authentication": False, "errors": []}

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
