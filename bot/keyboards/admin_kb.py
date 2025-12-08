from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🛠 Manage Products", callback_data="admin:products")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Manage Prices", callback_data="admin:prices")
    )
    builder.row(
        InlineKeyboardButton(text="🧑‍💼 Manage Resellers", callback_data="admin:resellers")
    )
    builder.row(
        InlineKeyboardButton(text="🎫 Manage Keys", callback_data="admin:keys")
    )
    builder.row(
        InlineKeyboardButton(text="💵 Manage Credits", callback_data="admin:credits")
    )
    builder.row(
        InlineKeyboardButton(text="🧑‍⚖ Manage Admins", callback_data="admin:admins")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Manage Sellers", callback_data="admin:sellers")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Statistics", callback_data="admin:stats")
    )
    return builder.as_markup()


def back_to_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def products_manage_keyboard(products: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for p in products:
        status = "✅" if p.get('is_active', True) else "❌"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {p['name']}", 
                callback_data=f"admin:product:{p['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ Add Product", callback_data="admin:product:add")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def product_manage_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Edit Name", callback_data=f"admin:product:edit_name:{product_id}"),
        InlineKeyboardButton(text="📝 Edit Description", callback_data=f"admin:product:edit_desc:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🖼 Set Image", callback_data=f"admin:product:set_image:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Manage Prices", callback_data=f"admin:product:prices:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Toggle Active", callback_data=f"admin:product:toggle:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Delete Product", callback_data=f"admin:product:delete:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Products", callback_data="admin:products")
    )
    return builder.as_markup()


def keys_manage_keyboard(products: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for p in products:
        builder.row(
            InlineKeyboardButton(
                text=f"🔑 {p['name']}", 
                callback_data=f"admin:keys:{p['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def product_keys_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Add Keys", callback_data=f"admin:keys:add:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📋 View Keys", callback_data=f"admin:keys:view:{product_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Keys", callback_data="admin:keys")
    )
    return builder.as_markup()


def resellers_keyboard(resellers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for r in resellers:
        name = r.get('username') or r.get('first_name', f"User {r['telegram_id']}")
        builder.row(
            InlineKeyboardButton(
                text=f"👤 {name}", 
                callback_data=f"admin:reseller:{r['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ Add Reseller", callback_data="admin:reseller:add")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def reseller_manage_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📦 View Orders", callback_data=f"admin:reseller:orders:{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Add Credits", callback_data=f"admin:credits:add:{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Remove Reseller", callback_data=f"admin:reseller:remove:{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Resellers", callback_data="admin:resellers")
    )
    return builder.as_markup()


def admins_keyboard(admins: list, root_admin_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for a in admins:
        name = a.get('username') or f"Admin {a['telegram_id']}"
        is_root = "👑" if a['telegram_id'] == root_admin_id else "🔑"
        builder.row(
            InlineKeyboardButton(
                text=f"{is_root} {name}", 
                callback_data=f"admin:admin:{a['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ Add Admin", callback_data="admin:admin:add")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def admin_manage_keyboard(admin_id: int, telegram_id: int, root_admin_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if telegram_id != root_admin_id:
        builder.row(
            InlineKeyboardButton(text="🗑 Remove Admin", callback_data=f"admin:admin:remove:{admin_id}")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="👑 Root Admin (Protected)", callback_data="noop")
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admins", callback_data="admin:admins")
    )
    return builder.as_markup()


def sellers_manage_keyboard(sellers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for s in sellers:
        builder.row(
            InlineKeyboardButton(
                text=f"⭐ @{s['username']}", 
                callback_data=f"admin:seller:{s['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ Add Seller", callback_data="admin:seller:add")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def seller_manage_keyboard(seller_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🗑 Remove Seller", callback_data=f"admin:seller:remove:{seller_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Sellers", callback_data="admin:sellers")
    )
    return builder.as_markup()


def confirm_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm:{action}:{item_id}"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="admin:back")
    )
    return builder.as_markup()


def credits_keyboard(users: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for u in users:
        name = u.get('username') or u.get('first_name', f"User {u['telegram_id']}")
        builder.row(
            InlineKeyboardButton(
                text=f"💰 {name} - ${u['balance']:.2f}", 
                callback_data=f"admin:credits:user:{u['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ Add by Telegram ID", callback_data="admin:credits:add_by_id")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin:back")
    )
    return builder.as_markup()


def user_credits_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Add Credits", callback_data=f"admin:credits:add:{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="➖ Remove Credits", callback_data=f"admin:credits:remove:{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Back to Credits", callback_data="admin:credits")
    )
    return builder.as_markup()
