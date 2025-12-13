from datetime import datetime
from typing import List, Optional


class Templates:
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    DIVIDER_THIN = "───────────────────────────"
    STAR_LINE = "✦━━━━━━━━━━━━━━━━━━━━━━━━✦"
    SPARKLE = "✨"
    
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
        status_text = "✨ Premium ✨" if status.lower() == "premium" else "Free"
        
        last_purchase_str = "Never" if not last_purchase else last_purchase.strftime("%Y-%m-%d %H:%M")
        
        return f"""
{Templates.welcome_banner()}
{Templates.STAR_LINE}
       👤 <b>Welcome, {first_name}!</b>
{Templates.STAR_LINE}

📋 <b>Your Profile</b>
{Templates.DIVIDER_THIN}
   🆔 Telegram ID: <code>{telegram_id}</code>
   💳 Balance: <code>${balance:.2f}</code>
   {status_emoji} Status: <b>{status_text}</b>
   📦 Last Purchase: {last_purchase_str}

{Templates.STAR_LINE}
      <i>Select an option below ⬇️</i>
{Templates.STAR_LINE}
"""
    
    @staticmethod
    def get_country_flag(country: str) -> str:
        """Get country flag emoji based on country name"""
        country_lower = country.lower()
        flags = {
            "india": "🇮🇳", "spain": "🇪🇸", "pakistan": "🇵🇰",
            "usa": "🇺🇸", "united states": "🇺🇸", "uk": "🇬🇧",
            "united kingdom": "🇬🇧", "germany": "🇩🇪", "france": "🇫🇷",
            "brazil": "🇧🇷", "russia": "🇷🇺", "indonesia": "🇮🇩",
            "philippines": "🇵🇭", "bangladesh": "🇧🇩", "china": "🇨🇳",
            "japan": "🇯🇵", "korea": "🇰🇷", "australia": "🇦🇺",
            "canada": "🇨🇦", "mexico": "🇲🇽", "italy": "🇮🇹",
            "turkey": "🇹🇷", "saudi": "🇸🇦", "uae": "🇦🇪",
            "egypt": "🇪🇬", "nigeria": "🇳🇬", "south africa": "🇿🇦"
        }
        for key, flag in flags.items():
            if key in country_lower:
                return flag
        return "🌍"
    
    @staticmethod
    def trusted_sellers(sellers: list) -> str:
        if not sellers:
            return "🎉 <b>Official sellers of Team Quantum!</b>\n\n<i>No trusted sellers available at the moment.</i>"
        
        sellers_by_country = {}
        for seller in sellers:
            country = seller.get("country") or "Other"
            if country not in sellers_by_country:
                sellers_by_country[country] = []
            sellers_by_country[country].append(seller)
        
        seller_text = "🎉 <b>Official sellers of Team Quantum!</b>\n"
        
        for country, country_sellers in sellers_by_country.items():
            flag = Templates.get_country_flag(country)
            seller_text += f"\n┌ <b>{country}</b> {flag}\n"
            
            for i, seller in enumerate(country_sellers, 1):
                name = seller.get("name") or seller.get("username", "Seller")
                username = seller.get("username", "")
                platforms = seller.get("platforms", "")
                
                seller_text += f"│\n│ {i}. <i>{name}</i>\n"
                
                if platforms:
                    for line in platforms.split('\n'):
                        line = line.strip()
                        if line:
                            seller_text += f"│ 💬 Contact: {line}\n"
                elif username:
                    seller_text += f"│ 💬 Contact: @{username}\n"
            
            seller_text += "└───────────────\n"
        
        seller_text += "\n✅ <i>Click below to contact Manager or Admin!</i>"
        
        return seller_text
    
    @staticmethod
    def products_list_free() -> str:
        return f"""
{Templates.STAR_LINE}
     🛍 <b>PRODUCTS</b>
{Templates.STAR_LINE}

🔒 <b>Premium Access Required</b>

<i>You need to upgrade to Premium to view 
product prices and make purchases.</i>

💎 Upgrade now to unlock:
   ✅ View all product prices
   ✅ Make purchases
   ✅ Access exclusive deals
   ✅ Priority support

{Templates.STAR_LINE}
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

📦 <b>Available Products:</b> {len(products)}

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
┌─────────────────────────┐
│ {i}. <b>{order['product_name']}</b>
│   📅 {date_str}
│   ⏱ {readable_duration}
│   💵 <code>${order['price']:.2f}</code>
"""
            if order.get('key'):
                order_text += f"│   🔑 <code>{order['key']}</code>\n"
            order_text += "└─────────────────────────┘\n"
        
        return f"""
{Templates.STAR_LINE}
     📦 <b>MY ORDERS</b>
{Templates.STAR_LINE}
{order_text}
{Templates.STAR_LINE}
"""
    
    @staticmethod
    def add_balance(manager_username: str, admin_username: str) -> str:
        return f"""
{Templates.STAR_LINE}
     💳 <b>ADD BALANCE</b>
{Templates.STAR_LINE}

To add balance to your account, please 
contact our manager or admin:

👤 <b>Manager:</b> {manager_username}
👤 <b>Admin:</b> {admin_username}

<i>Send the amount you wish to add and 
complete the payment as instructed.</i>

{Templates.STAR_LINE}
"""
    
    @staticmethod
    def upgrade_premium(admin_username: str) -> str:
        return f"""
{Templates.STAR_LINE}
     🚀 <b>UPGRADE TO PREMIUM</b>
{Templates.STAR_LINE}

💎 <b>Premium Benefits:</b>

   ✅ View all product prices
   ✅ Make purchases directly
   ✅ Access exclusive products
   ✅ Priority customer support
   ✅ Special discounts

📞 <b>To upgrade, contact:</b>
   {admin_username}

{Templates.STAR_LINE}
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
    def product_detail_user(product: dict, is_premium: bool = False) -> str:
        desc = product.get('description', 'No description available')
        stock = product.get('stock', 0)
        
        stock_section = ""
        if is_premium:
            stock_section = f"\n📦 <b>Stock Available:</b> {stock} keys\n"
        
        if is_premium:
            return f"""
{Templates.STAR_LINE}
     📦 <b>{product['name']}</b>
{Templates.STAR_LINE}

📝 <b>Description</b>
{Templates.DIVIDER_THIN}
{desc}
{stock_section}
💰 <b>Select Your Plan</b>
{Templates.DIVIDER_THIN}
<i>Choose a duration below to purchase:</i>

{Templates.STAR_LINE}
"""
        else:
            return f"""
{Templates.STAR_LINE}
     📦 <b>{product['name']}</b>
{Templates.STAR_LINE}

📝 <b>Description</b>
{Templates.DIVIDER_THIN}
{desc}

🔒 <b>Premium Required</b>
{Templates.DIVIDER_THIN}
<i>Upgrade to Premium to view prices and make purchases!</i>

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
    def broadcast_progress(total: int, sent: int, failed: int) -> str:
        remaining = total - sent - failed
        progress_pct = ((sent + failed) / total * 100) if total > 0 else 0
        
        # Create progress bar
        filled = int(progress_pct / 5)
        empty = 20 - filled
        bar = "█" * filled + "░" * empty
        
        return f"""
{Templates.DIVIDER}
📣 <b>BROADCAST IN PROGRESS</b>
{Templates.DIVIDER}

<code>[{bar}] {progress_pct:.1f}%</code>

📊 <b>Statistics:</b>
{Templates.DIVIDER_THIN}
   ✅ Sent: <code>{sent}</code>
   ⏳ Remaining: <code>{remaining}</code>
   ❌ Failed/Blocked: <code>{failed}</code>
   📝 Total: <code>{total}</code>

{Templates.DIVIDER}
"""
    
    @staticmethod
    def broadcast_complete(total: int, sent: int, failed: int) -> str:
        success_rate = (sent / total * 100) if total > 0 else 0
        
        return f"""
{Templates.DIVIDER}
✅ <b>BROADCAST COMPLETED!</b>
{Templates.DIVIDER}

📊 <b>Final Statistics:</b>
{Templates.DIVIDER_THIN}
   ✅ Successfully Sent: <code>{sent}</code>
   ❌ Failed/Blocked: <code>{failed}</code>
   📝 Total Users: <code>{total}</code>
   📈 Success Rate: <code>{success_rate:.1f}%</code>

{Templates.DIVIDER}
"""
    
    @staticmethod
    def top_sellers(sellers: list) -> str:
        if not sellers:
            return f"""
{Templates.DIVIDER}
🏆 <b>TOP SELLERS</b>
{Templates.DIVIDER}

<i>No sales data available yet.</i>

{Templates.DIVIDER}
"""
        
        seller_text = ""
        medals = ["🥇", "🥈", "🥉"]
        for i, seller in enumerate(sellers[:10], 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            name = seller.get('name') or seller.get('username') or f"User {seller.get('telegram_id', 'Unknown')}"
            total_spent = seller.get('total_spent', 0)
            orders_count = seller.get('orders_count', 0)
            
            seller_text += f"""
{medal} <b>{name}</b>
   💰 Total Spent: <code>${total_spent:.2f}</code>
   📦 Orders: <code>{orders_count}</code>
"""
        
        return f"""
{Templates.DIVIDER}
🏆 <b>TOP 10 SELLERS</b>
{Templates.DIVIDER}
{seller_text}
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
    
    @staticmethod
    def maintenance_mode() -> str:
        return f"""
╔══════════════════════════════════════╗
║                                      ║
║      🔧 <b>MAINTENANCE MODE</b> 🔧      ║
║                                      ║
╚══════════════════════════════════════╝

{Templates.STAR_LINE}

🚧 <b>We're Currently Under Maintenance</b>

<i>Our team is working hard to improve 
your experience. We'll be back shortly!</i>

{Templates.DIVIDER_THIN}

📢 <b>Stay Updated:</b>
Join our channel for updates 👇

🔗 <b>@TeamQuantumCH</b>

{Templates.DIVIDER_THIN}

⏳ <i>Thank you for your patience!</i>

{Templates.STAR_LINE}

💎 <b>Quantum Panel</b> - Premium Service
"""
    
    @staticmethod
    def user_banned(admin_username: str) -> str:
        return f"""
🚫 <b>Access Denied</b>

Your account has been suspended from using this bot.

If you believe this is a mistake, please contact our admin:

👤 <b>Admin:</b> {admin_username}

<i>We apologize for any inconvenience.</i>
"""
    
    @staticmethod
    def purchase_report(
        user_name: str,
        user_id: int,
        username: str,
        product_name: str,
        duration: str,
        price: float,
        key_value: str,
        new_balance: float,
        order_time: str
    ) -> str:
        readable_duration = Templates.get_readable_duration(duration)
        username_display = f"@{username}" if username else "N/A"
        
        return f"""🎉 <b>NEW PURCHASE</b>

👤 <b>{user_name}</b> ({username_display})
🆔 <code>{user_id}</code>

📦 {product_name} | {readable_duration}
💰 ${price:.2f}
🔑 <code>{key_value}</code>

💳 Balance: ${new_balance:.2f}
⏰ {order_time}"""
