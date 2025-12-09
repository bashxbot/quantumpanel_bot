from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List


def main_menu_keyboard(is_premium: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ Trusted Sellers", callback_data="trusted_sellers")
    )
    builder.row(
        InlineKeyboardButton(text="🛍 Products", callback_data="products")
    )
    builder.row(
        InlineKeyboardButton(text="💳 Add Balance", callback_data="add_balance"),
        InlineKeyboardButton(text="📦 My Orders", callback_data="my_orders")
    )
    if not is_premium:
        builder.row(
            InlineKeyboardButton(text="🚀 Upgrade to Premium", callback_data="upgrade_premium")
        )
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Menu", callback_data="back_to_menu")
    )
    return builder.as_markup()


def products_keyboard(products: list, is_premium: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for p in products:
        builder.row(
            InlineKeyboardButton(
                text=f"📦 {p['name']}", 
                callback_data=f"product:{p['id']}"
            )
        )
    
    if not is_premium:
        builder.row(
            InlineKeyboardButton(text="🚀 Upgrade to Premium", callback_data="upgrade_premium")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Menu", callback_data="back_to_menu")
    )
    return builder.as_markup()


def get_readable_duration(duration: str) -> str:
    """Convert duration to readable format. Handles both old format '7d|7 Days' and new format '7 Days'"""
    if '|' in duration:
        return duration.split('|')[1]
    return duration


def get_sort_key(duration: str) -> int:
    """Get sort key for duration to order prices properly. Handles both old and new formats."""
    import re
    
    # Handle old format with pipe (e.g., "1d|1 Day")
    if '|' in duration:
        code = duration.split('|')[0]
        match = re.match(r'^(\d+)(d|m)$', code)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            return num if unit == 'd' else num * 30
    
    # Handle new readable format (e.g., "1 Day", "3 Months")
    match = re.match(r'^(\d+)\s*(Day|Days|Month|Months)$', duration, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        unit = match.group(2).lower()
        if 'day' in unit:
            return num
        else:
            return num * 30
    
    return 999


def product_detail_keyboard(product_id: int, prices: list, is_premium: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    sorted_prices = sorted(prices, key=lambda p: get_sort_key(p['duration']))
    
    if is_premium:
        for price in sorted_prices:
            readable = get_readable_duration(price['duration'])
            in_stock = price.get('in_stock', True)
            if in_stock:
                builder.row(
                    InlineKeyboardButton(
                        text=f"🛒 {readable} — ${price['price']}",
                        callback_data=f"buy:{product_id}:{price['id']}"
                    )
                )
            else:
                builder.row(
                    InlineKeyboardButton(
                        text=f"❌ {readable} — OUT OF STOCK",
                        callback_data="noop"
                    )
                )
    else:
        for price in sorted_prices:
            readable = get_readable_duration(price['duration'])
            in_stock = price.get('in_stock', True)
            if in_stock:
                builder.row(
                    InlineKeyboardButton(
                        text=f"💰 {readable} — ${price['price']}",
                        callback_data="noop"
                    )
                )
            else:
                builder.row(
                    InlineKeyboardButton(
                        text=f"❌ {readable} — OUT OF STOCK",
                        callback_data="noop"
                    )
                )
        builder.row(
            InlineKeyboardButton(text="🚀 Upgrade to Purchase", callback_data="upgrade_premium")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Products", callback_data="products")
    )
    return builder.as_markup()


def confirm_purchase_keyboard(product_id: int, price_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Confirm Purchase",
            callback_data=f"confirm_buy:{product_id}:{price_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data=f"product:{product_id}")
    )
    return builder.as_markup()
