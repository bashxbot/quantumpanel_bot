from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List


def main_menu_keyboard() -> InlineKeyboardMarkup:
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
    
    if is_premium and products:
        for p in products:
            builder.row(
                InlineKeyboardButton(
                    text=f"📦 {p['name']}", 
                    callback_data=f"product:{p['id']}"
                )
            )
    elif not is_premium:
        builder.row(
            InlineKeyboardButton(text="🚀 Upgrade to Premium", callback_data="upgrade_premium")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Menu", callback_data="back_to_menu")
    )
    return builder.as_markup()


def product_detail_keyboard(product_id: int, prices: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for price in prices:
        builder.row(
            InlineKeyboardButton(
                text=f"🛒 Buy {price['duration']} - ${price['price']}",
                callback_data=f"buy:{product_id}:{price['id']}"
            )
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
