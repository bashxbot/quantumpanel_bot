from datetime import datetime
from typing import List, Optional


class Templates:
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIVIDER_THIN = "───────────────────────────"
    STAR_LINE = "✦━━━━━━━━━━━━━━━━━━━━━━━━✦"
    
    @staticmethod
    def get_readable_duration(duration: str) -> str:
        """Convert duration code like '7d|7 Days' to readable format"""
        if '|' in duration:
            return duration.split('|')[1]
        return duration
    
    @staticmethod
    def welcome_banner() -> str:
        return """
╔═══════════════════════════════════╗
║    🚀 <b>QUANTUM PANEL</b> 🚀       ║
║     Premium Service Center        ║
╚═══════════════════════════════════╝
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
{Templates.STAR_LINE}
     🛍 <b>PRODUCTS</b>
{Templates.STAR_LINE}

<i>No products available at the moment.</i>

{Templates.STAR_LINE}
"""
        
        return f"""
{Templates.STAR_LINE}
     🛍 <b>PRODUCTS</b>
{Templates.STAR_LINE}

<i>Select a product below to view details!</i>

{Templates.STAR_LINE}
"""
    
    @staticmethod
    def my_orders(orders: list) -> str:
        if not orders:
            return f"""
{Templates.STAR_LINE}
     📦 <b>MY ORDERS</b>
{Templates.STAR_LINE}

<i>You haven't made any purchases yet.</i>

{Templates.STAR_LINE}
"""
        
        order_text = ""
        for i, order in enumerate(orders, 1):
            date_str = order.get('date', 'Unknown')
            readable_duration = Templates.get_readable_duration(order['duration'])
            order_text += f"""
{i}. <b>{order['product_name']}</b>
   📅 {date_str}
   ⏱ {readable_duration}
   💵 <code>${order['price']:.2f}</code>
"""
            if order.get('key'):
                order_text += f"   🔑 <code>{order['key']}</code>\n"
        
        return f"""
{Templates.STAR_LINE}
     📦 <b>MY ORDERS</b>
{Templates.STAR_LINE}
{order_text}
{Templates.STAR_LINE}
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
        desc = product.get('description', 'No description available')
        
        return f"""
{Templates.STAR_LINE}
     📦 <b>{product['name']}</b>
{Templates.STAR_LINE}

📝 <b>Description</b>
{Templates.DIVIDER_THIN}
{desc}

💰 <b>Select Your Plan</b>
{Templates.DIVIDER_THIN}
<i>Choose a duration below to purchase:</i>

{Templates.STAR_LINE}
"""
    
    @staticmethod
    def purchase_summary(product_name: str, duration: str, price: float, current_balance: float) -> str:
        remaining = current_balance - price
        readable_duration = Templates.get_readable_duration(duration)
        
        return f"""
{Templates.STAR_LINE}
     🛒 <b>PURCHASE SUMMARY</b>
{Templates.STAR_LINE}

📦 <b>Product:</b> {product_name}
⏱ <b>Duration:</b> {readable_duration}
💵 <b>Price:</b> <code>${price:.2f}</code>

{Templates.DIVIDER_THIN}

💳 <b>Your Balance:</b> <code>${current_balance:.2f}</code>
💰 <b>After Purchase:</b> <code>${remaining:.2f}</code>

{Templates.STAR_LINE}

<i>Press confirm to complete your purchase!</i>
"""
    
    @staticmethod
    def purchase_success(product_name: str, duration: str, price: float, key_value: str = None, admin_contact: str = None) -> str:
        readable_duration = Templates.get_readable_duration(duration)
        
        key_section = ""
        if key_value:
            key_section = f"""
🔑 <b>Your Key:</b>
<code>{key_value}</code>

<i>Copy the key above and enjoy!</i>
"""
        else:
            key_section = f"""
📞 <b>Contact Admin:</b>
{admin_contact}

<i>Your key will be delivered shortly!</i>
"""
        
        return f"""
{Templates.STAR_LINE}
     ✅ <b>PURCHASE SUCCESSFUL!</b>
{Templates.STAR_LINE}

📦 <b>Product:</b> {product_name}
⏱ <b>Duration:</b> {readable_duration}
💵 <b>Paid:</b> <code>${price:.2f}</code>

{Templates.DIVIDER_THIN}

{key_section}

{Templates.STAR_LINE}
<i>Thank you for your purchase!</i>
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
