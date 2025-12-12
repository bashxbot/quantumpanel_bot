from aiohttp import web
import asyncio
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from bot.main import main as bot_main
from bot.database import async_session
from bot.services.user_service import UserService
from bot.services.admin_service import AdminService
from bot.services.product_service import ProductService
from bot.services.order_service import OrderService
from bot.services.seller_service import SellerService
from loguru import logger

WEB_USERS_FILE = "web_users.json"
TOKENS = {}

def load_web_users():
    if os.path.exists(WEB_USERS_FILE):
        with open(WEB_USERS_FILE, "r") as f:
            return json.load(f)
    default_users = {
        "users": [
            {
                "id": 1,
                "username": "admin",
                "password_hash": hashlib.sha256("quantumbotweb001".encode()).hexdigest(),
                "is_admin": True,
                "created_at": datetime.now().isoformat()
            }
        ]
    }
    save_web_users(default_users)
    return default_users

def save_web_users(data):
    with open(WEB_USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def verify_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    return TOKENS.get(token)

async def index_page(request):
    dist_path = os.path.join(os.path.dirname(__file__), 'client', 'dist', 'index.html')
    if os.path.exists(dist_path):
        return web.FileResponse(dist_path)
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    return web.FileResponse(html_path)

async def health_check(request):
    return web.Response(text="Bot is running", status=200)

async def auth_login(request):
    try:
        data = await request.json()
        username = data.get("username", "")
        password = data.get("password", "")
        
        web_users = load_web_users()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        for user in web_users["users"]:
            if user["username"] == username and user["password_hash"] == password_hash:
                token = secrets.token_urlsafe(32)
                TOKENS[token] = {"username": username, "isAdmin": user["is_admin"]}
                return web.json_response({
                    "success": True,
                    "token": token,
                    "user": {"username": username, "isAdmin": user["is_admin"]}
                })
        
        return web.json_response({"success": False, "error": "Invalid credentials"}, status=401)
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def auth_verify(request):
    user = verify_token(request)
    if user:
        return web.json_response({"valid": True, "user": user})
    return web.json_response({"valid": False}, status=401)

async def get_stats(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    async with async_session() as session:
        user_service = UserService(session)
        admin_service = AdminService(session)
        product_service = ProductService(session)
        order_service = OrderService(session)
        seller_service = SellerService(session)
        
        all_users = await user_service.get_all_users()
        premium_users = [u for u in all_users if u.is_premium]
        keys_data = await product_service.get_keys_count()
        products = await product_service.get_all_products(active_only=False)
        admins = await admin_service.get_all_admins()
        sellers = await seller_service.get_all_sellers(active_only=False)
        total_orders = await order_service.get_orders_count()
        total_revenue = await order_service.get_total_revenue()
        
        return web.json_response({
            "total_users": len(all_users),
            "premium_users": len(premium_users),
            "total_keys": keys_data["total"],
            "available_keys": keys_data["available"],
            "used_keys": keys_data["used"],
            "total_products": len(products),
            "total_admins": len(admins),
            "total_sellers": len(sellers),
            "total_orders": total_orders,
            "total_revenue": total_revenue
        })

async def get_keys(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    product_id = request.query.get("product_id")
    
    async with async_session() as session:
        product_service = ProductService(session)
        
        if product_id:
            keys = await product_service.get_keys_for_product(int(product_id))
            product = await product_service.get_product(int(product_id))
            keys_data = [
                {
                    "id": k.id,
                    "product_name": product.name if product else "Unknown",
                    "key_value": k.key_value,
                    "duration": k.duration,
                    "is_used": k.is_used,
                    "created_at": k.created_at.isoformat() if k.created_at else None
                }
                for k in keys[:100]
            ]
        else:
            products = await product_service.get_all_products(active_only=False)
            keys_data = []
            for p in products:
                keys = await product_service.get_keys_for_product(p.id)
                for k in keys[:50]:
                    keys_data.append({
                        "id": k.id,
                        "product_name": p.name,
                        "key_value": k.key_value,
                        "duration": k.duration,
                        "is_used": k.is_used,
                        "created_at": k.created_at.isoformat() if k.created_at else None
                    })
        
        return web.json_response({"keys": keys_data[:200]})

async def add_keys_bulk(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        product_id = data.get("product_id")
        keys_text = data.get("keys", "")
        
        async with async_session() as session:
            product_service = ProductService(session)
            product = await product_service.get_product(product_id)
            if not product:
                return web.json_response({"error": "Product not found"}, status=404)
            
            valid_durations = {p.duration for p in product.prices}
            added = 0
            
            for line in keys_text.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) != 2:
                    continue
                duration_code, key_value = parts
                duration = parse_duration_simple(duration_code)
                if duration and duration in valid_durations:
                    await product_service.add_key(product_id, key_value.strip(), duration)
                    added += 1
            
            return web.json_response({"success": True, "added": added})
    except Exception as e:
        logger.error(f"Add keys error: {e}")
        return web.json_response({"error": str(e)}, status=500)

def parse_duration_simple(code):
    import re
    match = re.match(r'^(\d+)(d|m)$', code.lower().strip())
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == 'd':
            return f"{num} Day{'s' if num > 1 else ''}"
        else:
            return f"{num} Month{'s' if num > 1 else ''}"
    return None

async def delete_keys_bulk(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        key_ids = data.get("key_ids", [])
        
        async with async_session() as session:
            product_service = ProductService(session)
            deleted = 0
            for kid in key_ids:
                if await product_service.remove_key(kid):
                    deleted += 1
            
            return web.json_response({"success": True, "deleted": deleted})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def delete_all_keys(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    product_id = int(request.match_info["product_id"])
    
    async with async_session() as session:
        product_service = ProductService(session)
        deleted = await product_service.delete_all_keys(product_id)
        return web.json_response({"success": True, "deleted": deleted})

async def delete_claimed_keys(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    product_id = int(request.match_info["product_id"])
    
    async with async_session() as session:
        product_service = ProductService(session)
        deleted = await product_service.delete_claimed_keys(product_id)
        return web.json_response({"success": True, "deleted": deleted})

async def get_products(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    async with async_session() as session:
        product_service = ProductService(session)
        products = await product_service.get_all_products(active_only=False)
        
        products_data = []
        for p in products:
            keys_data = await product_service.get_keys_count(p.id)
            products_data.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "is_active": p.is_active,
                "keys_count": keys_data["total"],
                "available_keys": keys_data["available"]
            })
        
        return web.json_response({"products": products_data})

async def create_product(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        async with async_session() as session:
            product_service = ProductService(session)
            product = await product_service.create_product(
                name=data.get("name"),
                description=data.get("description")
            )
            return web.json_response({"success": True, "id": product.id})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def toggle_product(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    product_id = int(request.match_info["product_id"])
    data = await request.json()
    
    async with async_session() as session:
        product_service = ProductService(session)
        await product_service.update_product(product_id, is_active=data.get("is_active"))
        return web.json_response({"success": True})

async def delete_product(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    product_id = int(request.match_info["product_id"])
    
    async with async_session() as session:
        product_service = ProductService(session)
        await product_service.delete_product(product_id)
        return web.json_response({"success": True})

async def get_admins(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    from bot.config import config
    
    async with async_session() as session:
        admin_service = AdminService(session)
        user_service = UserService(session)
        admins = await admin_service.get_all_admins()
        
        admins_data = []
        for a in admins:
            user = await user_service.get_user_by_telegram_id(a.telegram_id)
            admins_data.append({
                "id": a.id,
                "telegram_id": a.telegram_id,
                "username": a.username,
                "name": user.first_name if user else None,
                "is_root": a.telegram_id == config.bot.root_admin_id
            })
        
        return web.json_response({"admins": admins_data})

async def add_admin(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        telegram_id = data.get("telegram_id")
        
        async with async_session() as session:
            admin_service = AdminService(session)
            await admin_service.add_admin(telegram_id)
            return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def remove_admin(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    admin_id = int(request.match_info["admin_id"])
    
    async with async_session() as session:
        admin_service = AdminService(session)
        await admin_service.remove_admin_by_id(admin_id)
        return web.json_response({"success": True})

async def get_premium_users(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    async with async_session() as session:
        user_service = UserService(session)
        users = await user_service.get_all_users()
        premium = [u for u in users if u.is_premium]
        
        users_data = [{
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name
        } for u in premium]
        
        return web.json_response({"users": users_data})

async def add_premium_user(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        telegram_id = data.get("telegram_id")
        
        async with async_session() as session:
            user_service = UserService(session)
            await user_service.set_premium_by_telegram_id(telegram_id, True)
            return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def remove_premium_user(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    user_id = int(request.match_info["user_id"])
    
    async with async_session() as session:
        user_service = UserService(session)
        await user_service.remove_premium_by_id(user_id)
        return web.json_response({"success": True})

async def bulk_remove_premium(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        user_ids = data.get("user_ids", [])
        
        async with async_session() as session:
            user_service = UserService(session)
            for uid in user_ids:
                await user_service.remove_premium_by_id(uid)
            return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def get_sellers(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    async with async_session() as session:
        seller_service = SellerService(session)
        sellers = await seller_service.get_all_sellers(active_only=False)
        
        sellers_data = [{
            "id": s.id,
            "username": s.username,
            "name": s.name,
            "country": s.country,
            "platforms": s.platforms,
            "is_active": s.is_active
        } for s in sellers]
        
        return web.json_response({"sellers": sellers_data})

async def add_seller(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        async with async_session() as session:
            seller_service = SellerService(session)
            await seller_service.add_seller(
                username=data.get("username"),
                name=data.get("name"),
                country=data.get("country"),
                platforms=data.get("platforms")
            )
            return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def toggle_seller(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    seller_id = int(request.match_info["seller_id"])
    data = await request.json()
    
    async with async_session() as session:
        seller_service = SellerService(session)
        await seller_service.update_seller(seller_id, is_active=data.get("is_active"))
        return web.json_response({"success": True})

async def remove_seller(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    seller_id = int(request.match_info["seller_id"])
    
    async with async_session() as session:
        seller_service = SellerService(session)
        await seller_service.remove_seller(seller_id)
        return web.json_response({"success": True})

async def get_web_users(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    web_users = load_web_users()
    users_data = [{
        "id": u["id"],
        "username": u["username"],
        "is_admin": u["is_admin"],
        "created_at": u.get("created_at", datetime.now().isoformat())
    } for u in web_users["users"]]
    
    return web.json_response({"users": users_data})

async def add_web_user(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        web_users = load_web_users()
        
        new_id = max([u["id"] for u in web_users["users"]], default=0) + 1
        web_users["users"].append({
            "id": new_id,
            "username": data.get("username"),
            "password_hash": hashlib.sha256(data.get("password", "").encode()).hexdigest(),
            "is_admin": True,
            "created_at": datetime.now().isoformat()
        })
        
        save_web_users(web_users)
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def remove_web_user(request):
    if not verify_token(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    user_id = int(request.match_info["user_id"])
    web_users = load_web_users()
    web_users["users"] = [u for u in web_users["users"] if u["id"] != user_id]
    save_web_users(web_users)
    
    return web.json_response({"success": True})

async def serve_static(request):
    path = request.match_info.get("path", "")
    dist_path = os.path.join(os.path.dirname(__file__), 'client', 'dist', path)
    if os.path.exists(dist_path) and os.path.isfile(dist_path):
        return web.FileResponse(dist_path)
    return web.FileResponse(os.path.join(os.path.dirname(__file__), 'client', 'dist', 'index.html'))

async def start_web_server():
    app = web.Application()
    
    app.router.add_get('/health', health_check)
    app.router.add_post('/api/auth/login', auth_login)
    app.router.add_get('/api/auth/verify', auth_verify)
    app.router.add_get('/api/stats', get_stats)
    app.router.add_get('/api/keys', get_keys)
    app.router.add_post('/api/keys/bulk', add_keys_bulk)
    app.router.add_post('/api/keys/bulk-delete', delete_keys_bulk)
    app.router.add_delete('/api/keys/delete-all/{product_id}', delete_all_keys)
    app.router.add_delete('/api/keys/delete-claimed/{product_id}', delete_claimed_keys)
    app.router.add_get('/api/products', get_products)
    app.router.add_post('/api/products', create_product)
    app.router.add_post('/api/products/{product_id}/toggle', toggle_product)
    app.router.add_delete('/api/products/{product_id}', delete_product)
    app.router.add_get('/api/admins', get_admins)
    app.router.add_post('/api/admins', add_admin)
    app.router.add_delete('/api/admins/{admin_id}', remove_admin)
    app.router.add_get('/api/premium-users', get_premium_users)
    app.router.add_post('/api/premium-users', add_premium_user)
    app.router.add_delete('/api/premium-users/{user_id}', remove_premium_user)
    app.router.add_post('/api/premium-users/bulk-delete', bulk_remove_premium)
    app.router.add_get('/api/sellers', get_sellers)
    app.router.add_post('/api/sellers', add_seller)
    app.router.add_post('/api/sellers/{seller_id}/toggle', toggle_seller)
    app.router.add_delete('/api/sellers/{seller_id}', remove_seller)
    app.router.add_get('/api/web-users', get_web_users)
    app.router.add_post('/api/web-users', add_web_user)
    app.router.add_delete('/api/web-users/{user_id}', remove_web_user)
    
    dist_assets = os.path.join(os.path.dirname(__file__), 'client', 'dist', 'assets')
    if os.path.exists(dist_assets):
        app.router.add_static('/assets', dist_assets)
    
    app.router.add_get('/{path:.*}', serve_static)
    app.router.add_get('/', index_page)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    logger.info("Web server started on http://0.0.0.0:5000")

async def main():
    await asyncio.gather(
        start_web_server(),
        bot_main()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
