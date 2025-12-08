from datetime import datetime
from typing import List, Optional


class Templates:
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIVIDER_THIN = "─────────────────────────"
    
    @staticmethod
    def welcome_banner() -> str:
        return """
╔══════════════════════════════════╗
║   🚀 <b>QUANTUM PANEL</b> 🚀      ║
║    Premium Service Center        ║
╚══════════════════════════════════╝
"""
    
    @staticmethod
    def user_dashboard(
        first_name: str,
        telegram_id: int,
        balance: float,
        status: str,
        last_purchase: Optional[datetime] = None
    ) -> str:
        status_emoji = "⭐" if status.lower() == "premium" else "🆓"
        status_text = "Premium" if status.lower() == "premium" else "Free"
        
        last_purchase_str = "Never" if not last_purchase else last_purchase.strftime("%Y-%m-%d %H:%M")
        
        return f"""
{Templates.welcome_banner()}
{Templates.DIVIDER}
👤 <b>Welcome, {first_name}!</b>
{Templates.DIVIDER}

📋 <b>Your Profile</b>
{Templates.DIVIDER_THIN}
🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>
💳 <b>Balance:</b> <code>${balance:.2f}</code>
{status_emoji} <b>Status:</b> {status_text}
📦 <b>Last Purchase:</b> {last_purchase_str}
{Templates.DIVIDER}

<i>Select an option below:</i>
"""
    
    @staticmethod
    def trusted_sellers(sellers: list) -> str:
        if not sellers:
            return f"""
{Templates.DIVIDER}
⭐ <b>TRUSTED SELLERS</b>
{Templates.DIVIDER}

<i>No trusted sellers available at the moment.</i>

{Templates.DIVIDER}
"""
        
        seller_list = ""
        for i, seller in enumerate(sellers, 1):
            name = seller.get("name", seller.get("username", "Seller"))
            username = seller.get("username", "")
            desc = seller.get("description", "")
            seller_list += f"\n{i}. <b>{name}</b> - @{username}"
            if desc:
                seller_list += f"\n   <i>{desc}</i>"
            seller_list += "\n"
        
        return f"""
{Templates.DIVIDER}
⭐ <b>TRUSTED SELLERS</b>
{Templates.DIVIDER}
{seller_list}
{Templates.DIVIDER}
<i>Contact any seller above for assistance!</i>
"""
    
    @staticmethod
    def products_list_free() -> str:
        return f"""
{Templates.DIVIDER}
🛍 <b>PRODUCTS</b>
{Templates.DIVIDER}

🔒 <b>Premium Access Required</b>

<i>You need to upgrade to Premium to view 
product prices and make purchases.</i>

💎 Upgrade now to unlock:
   • View all product prices
   • Make purchases
   • Access exclusive deals
   • Priority support

{Templates.DIVIDER}
"""
    
    @staticmethod
    def products_list(products: list, is_premium: bool = False) -> str:
        if not is_premium:
            return Templates.products_list_free()
        
        if not products:
            return f"""
{Templates.DIVIDER}
🛍 <b>PRODUCTS</b>
{Templates.DIVIDER}

<i>No products available at the moment.</i>

{Templates.DIVIDER}
"""
        
        product_text = ""
        for p in products:
            product_text += f"\n📦 <b>{p['name']}</b>\n"
            if p.get('description'):
                product_text += f"   <i>{p['description']}</i>\n"
            if p.get('prices'):
                for price in p['prices']:
                    product_text += f"   • {price['duration']}: <code>${price['price']}</code>\n"
            product_text += "\n"
        
        return f"""
{Templates.DIVIDER}
🛍 <b>PRODUCTS</b>
{Templates.DIVIDER}
{product_text}
{Templates.DIVIDER}
<i>Select a product to purchase!</i>
"""
    
    @staticmethod
    def my_orders(orders: list) -> str:
        if not orders:
            return f"""
{Templates.DIVIDER}
📦 <b>MY ORDERS</b>
{Templates.DIVIDER}

<i>You haven't made any purchases yet.</i>

{Templates.DIVIDER}
"""
        
        order_text = ""
        for i, order in enumerate(orders, 1):
            date_str = order.get('date', 'Unknown')
            order_text += f"""
{i}. <b>{order['product_name']}</b>
   📅 {date_str}
   ⏱ Duration: {order['duration']}
   💰 Price: <code>${order['price']:.2f}</code>
"""
            if order.get('key'):
                order_text += f"   🔑 Key: <code>{order['key']}</code>\n"
        
        return f"""
{Templates.DIVIDER}
📦 <b>MY ORDERS</b> (Last 10)
{Templates.DIVIDER}
{order_text}
{Templates.DIVIDER}
"""
    
    @staticmethod
    def add_balance(admin_username: str) -> str:
        return f"""
{Templates.DIVIDER}
💳 <b>ADD BALANCE</b>
{Templates.DIVIDER}

To add balance to your account, please 
contact our admin:

👤 <b>Admin:</b> {admin_username}

<i>Send the amount you wish to add and 
complete the payment as instructed.</i>

{Templates.DIVIDER}
"""
    
    @staticmethod
    def upgrade_premium(admin_username: str) -> str:
        return f"""
{Templates.DIVIDER}
🚀 <b>UPGRADE TO PREMIUM</b>
{Templates.DIVIDER}

💎 <b>Premium Benefits:</b>

   ✅ View all product prices
   ✅ Make purchases directly
   ✅ Access exclusive products
   ✅ Priority customer support
   ✅ Special discounts

📞 <b>To upgrade, contact:</b>
   {admin_username}

{Templates.DIVIDER}
"""
    
    @staticmethod
    def admin_panel() -> str:
        return f"""
{Templates.DIVIDER}
👑 <b>ADMIN PANEL</b>
{Templates.DIVIDER}

Welcome to the Admin Control Center.
Select an option to manage your panel:

{Templates.DIVIDER}
"""
    
    @staticmethod
    def statistics(
        total_users: int,
        premium_users: int,
        total_orders: int,
        total_revenue: float,
        keys_available: int,
        keys_total: int,
        resellers_count: int
    ) -> str:
        return f"""
{Templates.DIVIDER}
📊 <b>STATISTICS</b>
{Templates.DIVIDER}

👥 <b>Users</b>
{Templates.DIVIDER_THIN}
   • Total Users: <code>{total_users}</code>
   • Premium Users: <code>{premium_users}</code>
   • Resellers: <code>{resellers_count}</code>

💰 <b>Revenue</b>
{Templates.DIVIDER_THIN}
   • Total Orders: <code>{total_orders}</code>
   • Total Revenue: <code>${total_revenue:.2f}</code>

🔑 <b>Keys Stock</b>
{Templates.DIVIDER_THIN}
   • Available Keys: <code>{keys_available}</code>
   • Total Keys: <code>{keys_total}</code>
   • Used Keys: <code>{keys_total - keys_available}</code>

{Templates.DIVIDER}
"""
    
    @staticmethod
    def product_detail(product: dict) -> str:
        prices_text = ""
        if product.get('prices'):
            for p in product['prices']:
                prices_text += f"\n   • {p['duration']}: <code>${p['price']}</code>"
        else:
            prices_text = "\n   <i>No prices set</i>"
        
        return f"""
{Templates.DIVIDER}
📦 <b>{product['name']}</b>
{Templates.DIVIDER}

📝 <b>Description:</b>
{product.get('description', 'No description')}

💰 <b>Prices:</b>{prices_text}

{Templates.DIVIDER}
"""
    
    @staticmethod
    def success(message: str) -> str:
        return f"✅ <b>Success!</b>\n\n{message}"
    
    @staticmethod
    def error(message: str) -> str:
        return f"❌ <b>Error!</b>\n\n{message}"
    
    @staticmethod
    def info(message: str) -> str:
        return f"ℹ️ <b>Info</b>\n\n{message}"
    
    @staticmethod
    def confirm(message: str) -> str:
        return f"⚠️ <b>Confirm Action</b>\n\n{message}"
