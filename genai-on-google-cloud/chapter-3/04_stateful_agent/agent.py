# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Stateful Agent - State Management with Three Scopes

This agent demonstrates ADK's state management system using a shopping cart
example, matching Examples 3-8, 3-9, and 3-10 from Chapter 3.

The three state scopes:
- temp: - Session-only state (lost when session ends)
- user: - User-specific state (persists across sessions for same user)
- app: - Application-wide state (shared across all users)

Key concepts:
- Using ToolContext to access state
- Different state scopes for different purposes
- State persistence patterns
- Policy-based expiry checking with app: state

Theme: SmartHome Customer Support (consistent with Chapter 3)
"""

from datetime import datetime, timedelta
from google.adk.agents import Agent
from google.adk.tools import ToolContext


# =============================================================================
# PRODUCT CATALOG (SmartHome Products)
# =============================================================================

PRODUCTS = {
    "SH-DOORBELL-PRO": {"name": "SmartHome Doorbell Pro", "price": 199.99, "category": "Security"},
    "SH-THERMOSTAT": {"name": "Smart Thermostat", "price": 149.99, "category": "Climate"},
    "SH-LOCK": {"name": "Smart Lock", "price": 249.99, "category": "Security"},
    "SH-LIGHT-4PK": {"name": "Smart Light Bulb 4-Pack", "price": 49.99, "category": "Lighting"},
    "SH-CAMERA-IN": {"name": "Indoor Security Camera", "price": 129.99, "category": "Security"},
    "SH-CAMERA-OUT": {"name": "Outdoor Security Camera", "price": 179.99, "category": "Security"},
    "SH-SPEAKER": {"name": "Smart Speaker Hub", "price": 99.99, "category": "Hub"},
}


# =============================================================================
# TOOLS WITH STATE MANAGEMENT (Examples 3-8, 3-9, 3-10)
# =============================================================================

def browse_products(category: str = None, tool_context: ToolContext = None) -> dict:
    """Browse available SmartHome products, optionally filtered by category.

    Args:
        category: Optional category to filter by (Security, Climate, Lighting, Hub)
        tool_context: Provided by ADK for state access

    Returns:
        List of available products
    """
    # Track browsing in temp state (session only)
    if tool_context:
        browse_count = tool_context.state.get("temp:browse_count", 0)
        tool_context.state["temp:browse_count"] = browse_count + 1
        tool_context.state["temp:last_action"] = f"Browsed {category or 'all'} products"

    if category:
        filtered = {
            pid: info for pid, info in PRODUCTS.items()
            if info["category"].lower() == category.lower()
        }
        return {
            "category": category,
            "products": filtered,
            "count": len(filtered)
        }

    return {
        "category": "all",
        "products": PRODUCTS,
        "count": len(PRODUCTS)
    }


# Example 3-8: State management with user: prefix
async def add_to_cart(product_id: str, tool_context: ToolContext, quantity: int = 1) -> dict:
    """Add a product to the user's shopping cart.

    Args:
        product_id: The product ID to add (e.g., "SH-DOORBELL-PRO")
        tool_context: Provided by ADK for state access
        quantity: Number of items to add (default 1)

    Returns:
        Updated cart information
    """
    if product_id not in PRODUCTS:
        return {"success": False, "error": f"Product {product_id} not found"}

    product = PRODUCTS[product_id]

    # Get current cart from user state (persists across sessions)
    cart = tool_context.state.get("user:cart", {"items": [], "total": 0.0})

    # Add item to cart
    cart["items"].append({
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "quantity": quantity
    })

    # Recalculate total
    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])

    # Save back to user state (Example 3-8)
    tool_context.state["user:cart"] = cart

    # Track in temp state (session only)
    tool_context.state["temp:last_action"] = f"Added {product['name']}"

    return {
        "success": True,
        "added": {"product": product["name"], "quantity": quantity},
        "cart_total": cart["total"]
    }


def view_cart(tool_context: ToolContext = None) -> dict:
    """View the current shopping cart contents.

    Args:
        tool_context: Provided by ADK for state access

    Returns:
        Current cart contents with totals
    """
    if tool_context:
        cart = tool_context.state.get("user:cart", {"items": [], "total": 0.0})
        tool_context.state["temp:last_action"] = "Viewed cart"

        if not cart["items"]:
            return {"message": "Your cart is empty", "items": [], "total": 0.0}

        return {
            "items": cart["items"],
            "total": cart["total"],
            "item_count": len(cart["items"])
        }

    return {"error": "State context not available"}


def remove_from_cart(product_id: str, tool_context: ToolContext = None) -> dict:
    """Remove a product from the shopping cart.

    Args:
        product_id: The product ID to remove
        tool_context: Provided by ADK for state access

    Returns:
        Updated cart information
    """
    if tool_context:
        cart = tool_context.state.get("user:cart", {"items": [], "total": 0.0})

        # Find and remove item
        original_count = len(cart["items"])
        cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]

        if len(cart["items"]) == original_count:
            return {"success": False, "error": f"Product {product_id} not in cart"}

        # Recalculate total
        cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])

        tool_context.state["user:cart"] = cart
        tool_context.state["temp:last_action"] = f"Removed {product_id}"

        return {
            "success": True,
            "removed": product_id,
            "cart_total": cart["total"],
            "cart_items": len(cart["items"])
        }

    return {"success": False, "error": "State context not available"}


# Example 3-10: Save cart for later with app: policy
async def save_cart_for_later(tool_context: ToolContext) -> dict:
    """Save the current cart for later retrieval.

    Uses app:saved_cart_expiry_days policy to determine how long
    saved carts are kept.

    Args:
        tool_context: Provided by ADK for state access

    Returns:
        Confirmation of saved cart
    """
    cart = tool_context.state.get("user:cart")

    if not cart or not cart.get("items"):
        # Temp state for validation status
        tool_context.state["temp:validation_status"] = "failed"
        return {"success": False, "error": "No cart to save"}

    # Save the cart with timestamp
    cart["saved_at"] = datetime.now().isoformat()
    tool_context.state["user:cart_saved"] = True
    tool_context.state["user:cart_saved_date"] = cart["saved_at"]
    tool_context.state["user:saved_cart"] = cart

    # Get expiry policy from app state
    expiry_days = tool_context.state.get("app:saved_cart_expiry_days", 30)

    tool_context.state["temp:validation_status"] = "success"

    return {
        "success": True,
        "message": "Cart saved for later",
        "saved_items": len(cart["items"]),
        "expires_in_days": expiry_days
    }


# Example 3-10: Check cart expiry using app: policy
async def check_cart_expiry(tool_context: ToolContext) -> dict:
    """Check if a saved cart has expired based on app policy.

    Uses app:saved_cart_expiry_days to determine validity.

    Args:
        tool_context: Provided by ADK for state access

    Returns:
        Cart validity status
    """
    saved_cart = tool_context.state.get("user:saved_cart")

    if not saved_cart:
        return {"has_saved_cart": False, "message": "No saved cart found"}

    # Get policy from app state (Example 3-10)
    max_days = tool_context.state.get("app:saved_cart_expiry_days", 30)

    saved_at_str = saved_cart.get("saved_at")
    if saved_at_str:
        saved_at = datetime.fromisoformat(saved_at_str)
        days_old = (datetime.now() - saved_at).days

        if days_old > max_days:
            return {
                "has_saved_cart": True,
                "expired": True,
                "days_old": days_old,
                "max_days": max_days,
                "message": f"Saved cart expired ({days_old} days old, max is {max_days})"
            }

        return {
            "has_saved_cart": True,
            "expired": False,
            "days_old": days_old,
            "days_remaining": max_days - days_old,
            "items": len(saved_cart.get("items", [])),
            "total": saved_cart.get("total", 0)
        }

    return {"has_saved_cart": True, "expired": False, "items": saved_cart.get("items", [])}


def restore_saved_cart(tool_context: ToolContext = None) -> dict:
    """Restore a previously saved cart.

    Args:
        tool_context: Provided by ADK for state access

    Returns:
        Restored cart contents
    """
    if tool_context:
        saved_cart = tool_context.state.get("user:saved_cart")

        if not saved_cart:
            return {"success": False, "error": "No saved cart to restore"}

        # Restore the cart
        tool_context.state["user:cart"] = saved_cart
        tool_context.state["temp:last_action"] = "Restored saved cart"

        return {
            "success": True,
            "message": "Cart restored",
            "items": len(saved_cart.get("items", [])),
            "total": saved_cart.get("total", 0)
        }

    return {"success": False, "error": "State context not available"}


def clear_cart(tool_context: ToolContext = None) -> dict:
    """Clear all items from the shopping cart.

    Args:
        tool_context: Provided by ADK for state access

    Returns:
        Confirmation of cleared cart
    """
    if tool_context:
        tool_context.state["user:cart"] = {"items": [], "total": 0.0}
        tool_context.state["temp:last_action"] = "Cleared cart"
        return {"success": True, "message": "Cart has been cleared"}

    return {"success": False, "error": "State context not available"}


def checkout(tool_context: ToolContext = None) -> dict:
    """Process checkout for the current cart.

    Args:
        tool_context: Provided by ADK for state access

    Returns:
        Order confirmation
    """
    if tool_context:
        cart = tool_context.state.get("user:cart", {"items": [], "total": 0.0})

        if not cart["items"]:
            return {"success": False, "error": "Cannot checkout with empty cart"}

        # Get order count from user state
        order_count = tool_context.state.get("user:order_count", 0)
        order_number = f"ORD-{order_count + 1:05d}"

        # Update user state
        tool_context.state["user:order_count"] = order_count + 1
        tool_context.state["user:last_order"] = {
            "order_number": order_number,
            "items": cart["items"],
            "total": cart["total"]
        }

        # Clear the cart
        tool_context.state["user:cart"] = {"items": [], "total": 0.0}
        tool_context.state["temp:last_action"] = f"Completed order {order_number}"

        return {
            "success": True,
            "order_number": order_number,
            "total_charged": cart["total"],
            "items_ordered": len(cart["items"]),
            "message": f"Order {order_number} confirmed! Thank you for your purchase."
        }

    return {"success": False, "error": "State context not available"}


# =============================================================================
# ROOT AGENT
# =============================================================================

root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="""You help customers with their SmartHome products.

You can help customers shop for SmartHome devices:
- Browse products by category (Security, Climate, Lighting, Hub)
- Add items to their shopping cart
- Save cart for later or restore saved cart
- View and manage their cart
- Complete checkout

Available products include doorbells, thermostats, locks, lights, cameras, and speakers.

State Management (for your understanding):
- Cart data persists across sessions (user comes back, cart is still there)
- Saved carts expire based on store policy (app:saved_cart_expiry_days)
- Session activity (like browse count) is temporary

Be helpful, suggest products based on what they're looking for, and guide them
through the shopping process. Always show prices and confirm before checkout.""",
    tools=[
        browse_products,
        add_to_cart,
        view_cart,
        remove_from_cart,
        save_cart_for_later,
        check_cart_expiry,
        restore_saved_cart,
        clear_cart,
        checkout
    ]
)
