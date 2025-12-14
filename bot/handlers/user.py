import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.enums import ParseMode, ContentType
from loguru import logger

from bot.database import async_session
from bot.services.user_service import UserService
from bot.services.product_service import ProductService
from bot.services.order_service import OrderService
from bot.services.seller_service import SellerService
from bot.templates.messages import Templates
from bot.keyboards.user_kb import (
    main_menu_keyboard,
    back_to_menu_keyboard,
    products_keyboard,
    product_detail_keyboard,
    confirm_purchase_keyboard,
    trusted_sellers_keyboard
)
from bot.config import config
from bot.models import UserStatus

router = Router()

BANNER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "banner.jpg")


async def check_banned(callback_or_message, user_id: int) -> bool:
    """Check if user is banned. Returns True if should block."""
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(user_id)
        
        if user and getattr(user, 'is_banned', False):
            text = Templates.user_banned(config.bot.admin_username)
            if hasattr(callback_or_message, 'message'):
                await callback_or_message.message.answer(text, parse_mode=ParseMode.HTML)
                await callback_or_message.answer()
            else:
                await callback_or_message.answer(text, parse_mode=ParseMode.HTML)
            return True
    return False


async def check_maintenance(callback_or_message, user_id: int) -> bool:
    """Check if maintenance mode is on and user is not admin. Returns True if should block."""
    if config.bot.maintenance_mode:
        if user_id != config.bot.root_admin_id:
            from bot.services.admin_service import AdminService
            async with async_session() as session:
                admin_service = AdminService(session)
                is_admin_user = await admin_service.is_admin(user_id)
            
            if not is_admin_user:
                text = Templates.maintenance_mode()
                if hasattr(callback_or_message, 'message'):
                    await callback_or_message.message.answer(text, parse_mode=ParseMode.HTML)
                    await callback_or_message.answer()
                else:
                    await callback_or_message.answer(text, parse_mode=ParseMode.HTML)
                return True
    return False


async def edit_message(callback: CallbackQuery, text: str, reply_markup=None):
    if callback.message.content_type == ContentType.PHOTO:
        await callback.message.edit_caption(
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )


@router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"👤 /start from user {message.from_user.id}")
    
    if await check_banned(message, message.from_user.id):
        return
    
    if await check_maintenance(message, message.from_user.id):
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        is_premium = user.status == UserStatus.PREMIUM
        
        text = Templates.user_dashboard(
            first_name=user.first_name or "User",
            telegram_id=user.telegram_id,
            balance=float(user.balance) if user.balance is not None else 0.0,
            status=user.status.value,
            last_purchase=user.last_purchase_at
        )
        
        if os.path.exists(BANNER_PATH):
            photo = FSInputFile(BANNER_PATH)
            await message.answer_photo(
                photo=photo,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(is_premium=is_premium)
            )
        else:
            await message.answer(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(is_premium=is_premium)
            )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name
        )
        
        is_premium = user.status == UserStatus.PREMIUM
        
        text = Templates.user_dashboard(
            first_name=user.first_name or "User",
            telegram_id=user.telegram_id,
            balance=float(user.balance) if user.balance is not None else 0.0,
            status=user.status.value,
            last_purchase=user.last_purchase_at
        )
        
        if callback.message.content_type == ContentType.PHOTO:
            chat_id = callback.message.chat.id
            try:
                await callback.message.delete()
            except Exception:
                pass
            
            if os.path.exists(BANNER_PATH):
                photo = FSInputFile(BANNER_PATH)
                await callback.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu_keyboard(is_premium=is_premium)
                )
            else:
                await callback.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu_keyboard(is_premium=is_premium)
                )
        else:
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(is_premium=is_premium)
            )
    await callback.answer()


@router.callback_query(F.data == "trusted_sellers")
async def show_trusted_sellers(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    async with async_session() as session:
        seller_service = SellerService(session)
        sellers = await seller_service.get_all_sellers(active_only=True)
        
        sellers_data = [
            {
                "username": s.username, 
                "name": s.name, 
                "description": s.description,
                "country": s.country,
                "platforms": s.platforms
            }
            for s in sellers
        ]
        
        text = Templates.trusted_sellers(sellers_data)
        
        chat_id = callback.message.chat.id
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=trusted_sellers_keyboard(config.bot.manager_username, config.bot.admin_username)
        )
    await callback.answer()


@router.callback_query(F.data == "products")
async def show_products(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        product_service = ProductService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        is_premium = user and user.status == UserStatus.PREMIUM
        
        products = await product_service.get_all_products(active_only=True)
        
        products_data = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "prices": [{"id": pr.id, "duration": pr.duration, "price": float(pr.price) if pr.price is not None else 0.0} for pr in p.prices]
            }
            for p in products
        ]
        
        text = Templates.products_list(products_data, is_premium=is_premium)
        keyboard = products_keyboard(products_data, is_premium=is_premium)
        
        if callback.message.content_type == ContentType.PHOTO:
            chat_id = callback.message.chat.id
            try:
                await callback.message.delete()
            except Exception:
                pass
            
            if os.path.exists(BANNER_PATH):
                photo = FSInputFile(BANNER_PATH)
                await callback.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
            else:
                await callback.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
        else:
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
    await callback.answer()


@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    product_id = int(callback.data.split(":")[1])
    
    async with async_session() as session:
        user_service = UserService(session)
        product_service = ProductService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        is_premium = user and user.status == UserStatus.PREMIUM
        
        product = await product_service.get_product(product_id)
        if not product:
            await callback.answer("❌ Product not found!", show_alert=True)
            return
        
        stock_per_duration = await product_service.get_stock_per_duration(product_id)
        
        prices_with_stock = []
        total_stock = 0
        for pr in product.prices:
            duration_stock = stock_per_duration.get(pr.duration, 0)
            # Ensure price is properly converted to float
            try:
                price_float = float(pr.price) if pr.price is not None else 0.0
            except (ValueError, TypeError):
                price_float = 0.0
            prices_with_stock.append({
                "id": pr.id, 
                "duration": pr.duration, 
                "price": price_float,
                "in_stock": duration_stock > 0
            })
            total_stock += duration_stock
        
        stock_count = await product_service.get_product_stock(product_id)
        
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "prices": prices_with_stock,
            "stock": stock_count
        }
        
        text = Templates.product_detail_user(product_data, is_premium=is_premium)
        keyboard = product_detail_keyboard(product_id, product_data["prices"], is_premium=is_premium, stock_per_duration=stock_per_duration)
        
        if product.image_file_id:
            from aiogram.types import InputMediaPhoto
            if callback.message.content_type == ContentType.PHOTO:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=product.image_file_id, caption=text, parse_mode=ParseMode.HTML),
                    reply_markup=keyboard
                )
            else:
                chat_id = callback.message.chat.id
                await callback.message.delete()
                await callback.bot.send_photo(
                    chat_id=chat_id,
                    photo=product.image_file_id,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
        else:
            await edit_message(callback, text, keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("buy:"))
async def initiate_purchase(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    parts = callback.data.split(":")
    product_id = int(parts[1])
    price_id = int(parts[2])
    
    async with async_session() as session:
        user_service = UserService(session)
        product_service = ProductService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user or user.status != UserStatus.PREMIUM:
            await callback.answer("⚠️ Premium access required!", show_alert=True)
            return
        
        product = await product_service.get_product(product_id)
        if not product:
            await callback.answer("❌ Product not found!", show_alert=True)
            return
        
        price = next((p for p in product.prices if p.id == price_id), None)
        if not price:
            await callback.answer("❌ Price option not found!", show_alert=True)
            return
        
        # Check if key is in stock
        key = await product_service.get_available_key(product_id, price.duration)
        if not key:
            await callback.answer("❌ Out of stock! Please try again later.", show_alert=True)
            return
        
        price_value = float(price.price)
        balance_value = float(user.balance)
        
        if balance_value < price_value:
            await callback.answer(f"❌ Insufficient balance! Need ${price_value:.2f}, have ${balance_value:.2f}", show_alert=True)
            return
        
        text = Templates.purchase_summary(
            product_name=product.name,
            duration=price.duration,
            price=price_value,
            current_balance=balance_value
        )
        
        await edit_message(callback, text, confirm_purchase_keyboard(product_id, price_id))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_buy:"))
async def confirm_purchase(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    parts = callback.data.split(":")
    product_id = int(parts[1])
    price_id = int(parts[2])
    
    async with async_session() as session:
        user_service = UserService(session)
        product_service = ProductService(session)
        order_service = OrderService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("❌ User not found!", show_alert=True)
            return
        
        product = await product_service.get_product(product_id)
        if not product:
            await callback.answer("❌ Product not found!", show_alert=True)
            return
        
        price = next((p for p in product.prices if p.id == price_id), None)
        if not price:
            await callback.answer("❌ Price option not found!", show_alert=True)
            return
        
        price_value = float(price.price)
        balance_value = float(user.balance)
        
        if balance_value < price_value:
            await callback.answer("❌ Insufficient balance!", show_alert=True)
            return
        
        key = await product_service.get_available_key(product_id, price.duration)
        if not key:
            await callback.answer("❌ Out of stock! No keys available.", show_alert=True)
            return
        
        key_value = key.key_value
        await product_service.mark_key_used(key.id)
        
        order = await order_service.create_order(
            user_id=user.id,
            product_id=product_id,
            product_name=product.name,
            duration=price.duration,
            price=price_value,
            key_value=key_value
        )
        
        await user_service.update_balance(user.id, -price_value)
        new_balance = balance_value - price_value
        
        success_msg = Templates.purchase_success(
            product_name=product.name,
            duration=price.duration,
            price=price_value,
            key_value=key_value,
            admin_contact=config.bot.admin_username
        )
        
        logger.info(f"✅ Purchase completed: User {user.telegram_id} bought {product.name}")
        
        try:
            from datetime import datetime
            report_channel = config.bot.report_channel
            if report_channel and report_channel.strip():
                channel_id = report_channel.strip()
                if "t.me/" in report_channel:
                    channel_part = report_channel.split("t.me/")[1]
                    if channel_part.startswith("+"):
                        pass
                    elif not channel_part.startswith("@") and not channel_part.startswith("-"):
                        channel_id = "@" + channel_part
                    else:
                        channel_id = channel_part
                
                if channel_id:
                    report_msg = Templates.purchase_report(
                        user_name=user.first_name or "User",
                        user_id=user.telegram_id,
                        username=user.username or "",
                        product_name=product.name,
                        duration=price.duration,
                        price=price_value,
                        key_value=key_value,
                        new_balance=new_balance,
                        order_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    
                    await callback.bot.send_message(
                        chat_id=channel_id,
                        text=report_msg,
                        parse_mode=ParseMode.HTML
                    )
        except Exception as e:
            logger.error(f"Failed to send purchase report: {e}")
        
        await edit_message(callback, success_msg, back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "my_orders")
async def show_my_orders(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        order_service = OrderService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("❌ User not found!", show_alert=True)
            return
        
        orders = await order_service.get_user_orders(user.id, limit=10)
        
        orders_data = [
            {
                "product_name": o.product_name,
                "duration": o.duration,
                "price": o.price,
                "key": o.key_value,
                "date": o.purchased_at.strftime("%Y-%m-%d %H:%M") if o.purchased_at else "Unknown"
            }
            for o in orders
        ]
        
        text = Templates.my_orders(orders_data)
        
        await edit_message(callback, text, back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "add_balance")
async def show_add_balance(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    text = Templates.add_balance(config.bot.manager_username, config.bot.admin_username)
    
    await edit_message(callback, text, back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "upgrade_premium")
async def show_upgrade_premium(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if await check_maintenance(callback, callback.from_user.id):
        return
    
    text = Templates.upgrade_premium(config.bot.admin_username)
    
    await edit_message(callback, text, back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
