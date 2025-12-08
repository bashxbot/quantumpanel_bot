from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from bot.database import async_session
from bot.services.user_service import UserService
from bot.services.admin_service import AdminService
from bot.services.product_service import ProductService
from bot.services.order_service import OrderService
from bot.services.seller_service import SellerService
from bot.templates.messages import Templates
from bot.keyboards.admin_kb import (
    admin_main_keyboard,
    back_to_admin_keyboard,
    products_manage_keyboard,
    product_manage_keyboard,
    keys_manage_keyboard,
    product_keys_keyboard,
    resellers_keyboard,
    reseller_manage_keyboard,
    admins_keyboard,
    admin_manage_keyboard,
    sellers_manage_keyboard,
    seller_manage_keyboard,
    credits_keyboard,
    user_credits_keyboard,
    premium_users_keyboard,
    premium_user_manage_keyboard
)
from bot.config import config

router = Router()


class AdminStates(StatesGroup):
    waiting_product_name = State()
    waiting_product_description = State()
    waiting_product_image = State()
    waiting_price_duration = State()
    waiting_price_amount = State()
    waiting_keys = State()
    waiting_admin_id = State()
    waiting_reseller_id = State()
    waiting_seller_username = State()
    waiting_seller_name = State()
    waiting_credit_amount = State()
    waiting_user_telegram_id = State()
    waiting_premium_user_id = State()


async def is_admin_check(user_id: int) -> bool:
    async with async_session() as session:
        admin_service = AdminService(session)
        return await admin_service.is_admin(user_id)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not await is_admin_check(message.from_user.id):
        logger.warning(f"⚠️ Unauthorized admin access attempt: {message.from_user.id}")
        return
    
    logger.info(f"👑 Admin panel accessed by {message.from_user.id}")
    
    text = Templates.admin_panel()
    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard()
    )


@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.clear()
    text = Templates.admin_panel()
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def show_statistics(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        order_service = OrderService(session)
        product_service = ProductService(session)
        
        all_users = await user_service.get_all_users()
        premium_count = await user_service.get_premium_users_count()
        resellers = await user_service.get_resellers()
        total_orders = await order_service.get_orders_count()
        total_revenue = await order_service.get_total_revenue()
        keys_data = await product_service.get_keys_count()
        
        text = Templates.statistics(
            total_users=len(all_users),
            premium_users=premium_count,
            total_orders=total_orders,
            total_revenue=total_revenue,
            keys_available=keys_data["available"],
            keys_total=keys_data["total"],
            resellers_count=len(resellers)
        )
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "admin:products")
async def manage_products(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        product_service = ProductService(session)
        products = await product_service.get_all_products(active_only=False)
        
        products_data = [
            {"id": p.id, "name": p.name, "is_active": p.is_active}
            for p in products
        ]
        
        text = f"""
{Templates.DIVIDER}
🛠 <b>MANAGE PRODUCTS</b>
{Templates.DIVIDER}

Total products: {len(products)}

Select a product to manage:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=products_manage_keyboard(products_data)
        )
    await callback.answer()


@router.callback_query(F.data == "admin:product:add")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_product_name)
    
    await callback.message.edit_text(
        Templates.info("Please send the <b>product name</b>:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_product_name)
async def add_product_name(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    await state.update_data(product_name=message.text)
    await state.set_state(AdminStates.waiting_product_description)
    
    await message.answer(
        Templates.info("Now send the <b>product description</b> (or send /skip to skip):"),
        parse_mode=ParseMode.HTML
    )


@router.message(AdminStates.waiting_product_description)
async def add_product_description(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    description = None if message.text == "/skip" else message.text
    
    async with async_session() as session:
        product_service = ProductService(session)
        product = await product_service.create_product(
            name=data["product_name"],
            description=description
        )
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"Product <b>{product.name}</b> created successfully!"),
            parse_mode=ParseMode.HTML,
            reply_markup=product_manage_keyboard(product.id)
        )


@router.callback_query(F.data.startswith("admin:product:") & ~F.data.contains("add"))
async def manage_single_product(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    action = parts[2] if len(parts) > 2 else None
    product_id = int(parts[3]) if len(parts) > 3 else int(parts[2]) if parts[2].isdigit() else None
    
    if action == "toggle" and product_id:
        async with async_session() as session:
            product_service = ProductService(session)
            product = await product_service.get_product(product_id)
            if product:
                await product_service.update_product(product_id, is_active=not product.is_active)
                await callback.answer(f"{'✅ Activated' if not product.is_active else '❌ Deactivated'}")
                callback.data = "admin:products"
                return await manage_products(callback)
    
    elif action == "delete" and product_id:
        async with async_session() as session:
            product_service = ProductService(session)
            await product_service.delete_product(product_id)
            await callback.answer("🗑 Product deleted!")
            callback.data = "admin:products"
            return await manage_products(callback)
    
    elif action == "edit_name" and product_id:
        await state.set_state(AdminStates.waiting_product_name)
        await state.update_data(editing_product_id=product_id)
        await callback.message.edit_text(
            Templates.info("Send the new product name:"),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return
    
    elif action == "prices" and product_id:
        await state.update_data(current_product_id=product_id)
        await state.set_state(AdminStates.waiting_price_duration)
        await callback.message.edit_text(
            Templates.info("Send the duration name (e.g., '1 Month', '3 Months', 'Lifetime'):"),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return
    
    elif product_id:
        async with async_session() as session:
            product_service = ProductService(session)
            product = await product_service.get_product(product_id)
            
            if product:
                product_data = {
                    "name": product.name,
                    "description": product.description,
                    "prices": [{"duration": p.duration, "price": p.price} for p in product.prices]
                }
                text = Templates.product_detail(product_data)
                
                await callback.message.edit_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=product_manage_keyboard(product_id)
                )
    
    await callback.answer()


@router.message(AdminStates.waiting_price_duration)
async def add_price_duration(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    await state.update_data(price_duration=message.text)
    await state.set_state(AdminStates.waiting_price_amount)
    
    await message.answer(
        Templates.info("Now send the <b>price</b> (number only):"),
        parse_mode=ParseMode.HTML
    )


@router.message(AdminStates.waiting_price_amount)
async def add_price_amount(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    try:
        price = int(message.text)
    except ValueError:
        await message.answer(Templates.error("Please send a valid number!"), parse_mode=ParseMode.HTML)
        return
    
    data = await state.get_data()
    
    async with async_session() as session:
        product_service = ProductService(session)
        await product_service.add_price(
            product_id=data["current_product_id"],
            duration=data["price_duration"],
            price=price
        )
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"Price added: {data['price_duration']} - ${price}"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data == "admin:keys")
async def manage_keys(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        product_service = ProductService(session)
        products = await product_service.get_all_products(active_only=False)
        
        products_data = [{"id": p.id, "name": p.name} for p in products]
        
        text = f"""
{Templates.DIVIDER}
🎫 <b>MANAGE KEYS</b>
{Templates.DIVIDER}

Select a product to manage keys:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keys_manage_keyboard(products_data)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:keys:"))
async def manage_product_keys(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    action = parts[2] if len(parts) > 2 else None
    product_id = int(parts[3]) if len(parts) > 3 else None
    
    if action == "add" and product_id:
        await state.update_data(keys_product_id=product_id)
        await state.set_state(AdminStates.waiting_keys)
        await callback.message.edit_text(
            Templates.info(
                "Send keys in this format:\n\n"
                "<code>DURATION|KEY</code>\n\n"
                "Example:\n"
                "<code>1 Month|ABC123XYZ</code>\n"
                "<code>3 Months|DEF456UVW</code>\n\n"
                "Send multiple lines to add multiple keys."
            ),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return
    
    elif action == "view" and product_id:
        async with async_session() as session:
            product_service = ProductService(session)
            keys = await product_service.get_keys_for_product(product_id)
            
            if not keys:
                await callback.answer("No keys found for this product!", show_alert=True)
                return
            
            text = f"{Templates.DIVIDER}\n🔑 <b>KEYS</b>\n{Templates.DIVIDER}\n\n"
            for k in keys[:20]:
                status = "✅" if not k.is_used else "❌"
                text += f"{status} {k.duration}: <code>{k.key_value[:20]}...</code>\n"
            
            if len(keys) > 20:
                text += f"\n... and {len(keys) - 20} more keys"
            
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=product_keys_keyboard(product_id)
            )
        await callback.answer()
        return
    
    elif product_id or (action and action.isdigit()):
        pid = product_id or int(action)
        async with async_session() as session:
            product_service = ProductService(session)
            keys_data = await product_service.get_keys_count(pid)
            product = await product_service.get_product(pid)
            
            text = f"""
{Templates.DIVIDER}
🔑 <b>{product.name} - KEYS</b>
{Templates.DIVIDER}

📊 <b>Statistics:</b>
   • Total: {keys_data['total']}
   • Available: {keys_data['available']}
   • Used: {keys_data['used']}
"""
            
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=product_keys_keyboard(pid)
            )
    
    await callback.answer()


@router.message(AdminStates.waiting_keys)
async def add_keys(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    product_id = data.get("keys_product_id")
    
    lines = message.text.strip().split("\n")
    added = 0
    
    async with async_session() as session:
        product_service = ProductService(session)
        
        for line in lines:
            if "|" in line:
                parts = line.split("|", 1)
                if len(parts) == 2:
                    duration = parts[0].strip()
                    key_value = parts[1].strip()
                    await product_service.add_key(product_id, key_value, duration)
                    added += 1
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"Added {added} keys successfully!"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data == "admin:resellers")
async def manage_resellers(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        resellers = await user_service.get_resellers()
        
        resellers_data = [
            {
                "id": r.id,
                "telegram_id": r.telegram_id,
                "username": r.username,
                "first_name": r.first_name,
                "balance": r.balance
            }
            for r in resellers
        ]
        
        text = f"""
{Templates.DIVIDER}
🧑‍💼 <b>MANAGE RESELLERS</b>
{Templates.DIVIDER}

Total resellers: {len(resellers)}

Select a reseller to manage:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=resellers_keyboard(resellers_data)
        )
    await callback.answer()


@router.callback_query(F.data == "admin:reseller:add")
async def add_reseller_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_reseller_id)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>Telegram ID</b> of the user to add as reseller:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_reseller_id)
async def add_reseller(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    try:
        telegram_id = int(message.text)
    except ValueError:
        await message.answer(Templates.error("Please send a valid Telegram ID!"), parse_mode=ParseMode.HTML)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer(
                Templates.error("User not found! They need to start the bot first."),
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_admin_keyboard()
            )
            await state.clear()
            return
        
        await user_service.set_reseller(user.id, True)
        await user_service.set_premium(user.id, True)
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"User {user.first_name or telegram_id} is now a reseller!"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data.startswith("admin:reseller:remove:"))
async def remove_reseller(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        user_service = UserService(session)
        await user_service.set_reseller(user_id, False)
        
        await callback.answer("✅ Reseller removed!")
        callback.data = "admin:resellers"
        return await manage_resellers(callback)


@router.callback_query(F.data == "admin:admins")
async def manage_admins(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        admin_service = AdminService(session)
        admins = await admin_service.get_all_admins()
        
        admins_data = [
            {"id": a.id, "telegram_id": a.telegram_id, "username": a.username}
            for a in admins
        ]
        
        text = f"""
{Templates.DIVIDER}
🧑‍⚖ <b>MANAGE ADMINS</b>
{Templates.DIVIDER}

Total admins: {len(admins)}

Select an admin to manage:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=admins_keyboard(admins_data, config.bot.root_admin_id)
        )
    await callback.answer()


@router.callback_query(F.data == "admin:admin:add")
async def add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_admin_id)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>Telegram ID</b> of the user to add as admin:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_admin_id)
async def add_admin(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    try:
        telegram_id = int(message.text)
    except ValueError:
        await message.answer(Templates.error("Please send a valid Telegram ID!"), parse_mode=ParseMode.HTML)
        return
    
    async with async_session() as session:
        admin_service = AdminService(session)
        success = await admin_service.add_admin(telegram_id)
        
        await state.clear()
        
        if success:
            await message.answer(
                Templates.success(f"Admin {telegram_id} added successfully!"),
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_admin_keyboard()
            )
        else:
            await message.answer(
                Templates.error("This user is already an admin!"),
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_admin_keyboard()
            )


@router.callback_query(F.data.startswith("admin:admin:remove:"))
async def remove_admin(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    admin_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        admin_service = AdminService(session)
        admin = await admin_service.get_all_admins()
        target = next((a for a in admin if a.id == admin_id), None)
        
        if target and target.telegram_id == config.bot.root_admin_id:
            await callback.answer("❌ Cannot remove root admin!", show_alert=True)
            return
        
        if target:
            await admin_service.remove_admin(target.telegram_id)
            await callback.answer("✅ Admin removed!")
        
        callback.data = "admin:admins"
        return await manage_admins(callback)


@router.callback_query(F.data == "admin:sellers")
async def manage_sellers(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        seller_service = SellerService(session)
        sellers = await seller_service.get_all_sellers()
        
        sellers_data = [
            {"id": s.id, "username": s.username, "name": s.name}
            for s in sellers
        ]
        
        text = f"""
{Templates.DIVIDER}
⭐ <b>MANAGE TRUSTED SELLERS</b>
{Templates.DIVIDER}

Total sellers: {len(sellers)}

Select a seller to manage:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=sellers_manage_keyboard(sellers_data)
        )
    await callback.answer()


@router.callback_query(F.data == "admin:seller:add")
async def add_seller_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_seller_username)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>username</b> of the seller (without @):"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_seller_username)
async def add_seller_username(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    username = message.text.replace("@", "").strip()
    await state.update_data(seller_username=username)
    await state.set_state(AdminStates.waiting_seller_name)
    
    await message.answer(
        Templates.info("Now send the seller's <b>display name</b> (or /skip):"),
        parse_mode=ParseMode.HTML
    )


@router.message(AdminStates.waiting_seller_name)
async def add_seller_name(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    name = None if message.text == "/skip" else message.text
    
    async with async_session() as session:
        seller_service = SellerService(session)
        await seller_service.add_seller(
            username=data["seller_username"],
            name=name
        )
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"Seller @{data['seller_username']} added!"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data.startswith("admin:seller:remove:"))
async def remove_seller(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    seller_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        seller_service = SellerService(session)
        await seller_service.remove_seller(seller_id)
        
        await callback.answer("✅ Seller removed!")
        callback.data = "admin:sellers"
        return await manage_sellers(callback)


@router.callback_query(F.data == "admin:credits")
async def manage_credits(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        users = await user_service.get_all_users()
        
        users_data = [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "balance": u.balance
            }
            for u in users[:20]
        ]
        
        text = f"""
{Templates.DIVIDER}
💵 <b>MANAGE CREDITS</b>
{Templates.DIVIDER}

Select a user to manage credits:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=credits_keyboard(users_data)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:credits:user:"))
async def show_user_credits(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        user_service = UserService(session)
        users = await user_service.get_all_users()
        user = next((u for u in users if u.id == user_id), None)
        
        if user:
            text = f"""
{Templates.DIVIDER}
💵 <b>USER CREDITS</b>
{Templates.DIVIDER}

👤 <b>User:</b> {user.first_name or user.username or user.telegram_id}
🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>
💰 <b>Balance:</b> <code>${user.balance:.2f}</code>
"""
            
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=user_credits_keyboard(user_id)
            )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:credits:add:"))
async def add_credits_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    await state.update_data(credit_user_id=user_id, credit_action="add")
    await state.set_state(AdminStates.waiting_credit_amount)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>amount</b> to add:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:credits:remove:"))
async def remove_credits_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    await state.update_data(credit_user_id=user_id, credit_action="remove")
    await state.set_state(AdminStates.waiting_credit_amount)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>amount</b> to remove:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_credit_amount)
async def process_credits(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer(Templates.error("Please send a valid amount!"), parse_mode=ParseMode.HTML)
        return
    
    data = await state.get_data()
    user_id = data["credit_user_id"]
    action = data["credit_action"]
    
    if action == "remove":
        amount = -amount
    
    async with async_session() as session:
        user_service = UserService(session)
        await user_service.update_balance(user_id, amount)
        
        await state.clear()
        
        action_text = "added to" if action == "add" else "removed from"
        await message.answer(
            Templates.success(f"${abs(amount):.2f} {action_text} user balance!"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data == "admin:credits:add_by_id")
async def add_credits_by_id_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_user_telegram_id)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>Telegram ID</b> of the user:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_user_telegram_id)
async def add_credits_by_id(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    try:
        telegram_id = int(message.text)
    except ValueError:
        await message.answer(Templates.error("Please send a valid Telegram ID!"), parse_mode=ParseMode.HTML)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer(
                Templates.error("User not found!"),
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_admin_keyboard()
            )
            await state.clear()
            return
        
        await state.update_data(credit_user_id=user.id, credit_action="add")
        await state.set_state(AdminStates.waiting_credit_amount)
        
        await message.answer(
            Templates.info(f"User found: {user.first_name or telegram_id}\nCurrent balance: ${user.balance:.2f}\n\nSend the amount to add:"),
            parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "admin:prices")
async def manage_prices(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    callback.data = "admin:products"
    return await manage_products(callback)


@router.callback_query(F.data == "admin:premium")
async def manage_premium_users(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        all_users = await user_service.get_all_users()
        premium_users = [u for u in all_users if u.status.value == "premium"]
        
        users_data = [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "first_name": u.first_name,
                "balance": u.balance
            }
            for u in premium_users
        ]
        
        text = f"""
{Templates.DIVIDER}
⭐ <b>MANAGE PREMIUM USERS</b>
{Templates.DIVIDER}

Total premium users: {len(premium_users)}

Select a user to manage:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=premium_users_keyboard(users_data)
        )
    await callback.answer()


@router.callback_query(F.data == "admin:premium:add")
async def add_premium_user_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_premium_user_id)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>Telegram ID</b> of the user to add premium status:"),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.message(AdminStates.waiting_premium_user_id)
async def add_premium_user(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    try:
        telegram_id = int(message.text)
    except ValueError:
        await message.answer(Templates.error("Please send a valid Telegram ID!"), parse_mode=ParseMode.HTML)
        return
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer(
                Templates.error("User not found! They need to start the bot first."),
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_admin_keyboard()
            )
            await state.clear()
            return
        
        await user_service.set_premium(user.id, True)
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"User {user.first_name or telegram_id} is now a Premium user! ⭐"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data.startswith("admin:premium:user:"))
async def show_premium_user(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        user_service = UserService(session)
        users = await user_service.get_all_users()
        user = next((u for u in users if u.id == user_id), None)
        
        if user:
            text = f"""
{Templates.DIVIDER}
⭐ <b>PREMIUM USER</b>
{Templates.DIVIDER}

👤 <b>Name:</b> {user.first_name or 'N/A'}
🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>
👤 <b>Username:</b> @{user.username or 'N/A'}
💰 <b>Balance:</b> <code>${user.balance:.2f}</code>
⭐ <b>Status:</b> {user.status.value.title()}
"""
            
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=premium_user_manage_keyboard(user_id)
            )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:premium:remove:"))
async def remove_premium_user(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        user_service = UserService(session)
        await user_service.set_premium(user_id, False)
        
        await callback.answer("✅ Premium status removed!")
        callback.data = "admin:premium"
        return await manage_premium_users(callback)
