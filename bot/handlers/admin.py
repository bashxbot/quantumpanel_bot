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
    admins_keyboard,
    admin_manage_keyboard,
    sellers_manage_keyboard,
    seller_manage_keyboard,
    credits_keyboard,
    user_credits_keyboard,
    premium_users_keyboard,
    premium_user_manage_keyboard,
    broadcast_keyboard,
    broadcast_cancel_keyboard,
    statistics_keyboard,
    user_management_keyboard,
    broadcast_cancel_inline_keyboard
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
    waiting_seller_username = State()
    waiting_seller_name = State()
    waiting_seller_description = State()
    waiting_seller_platforms = State()
    waiting_seller_country = State()
    waiting_credit_amount = State()
    waiting_user_telegram_id = State()
    waiting_premium_user_id = State()
    waiting_broadcast_text = State()
    waiting_broadcast_photo = State()
    waiting_usermgmt_user = State()
    waiting_usermgmt_amount = State()

broadcast_cancelled = {}


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
            resellers_count=0
        )
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=statistics_keyboard()
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
    
    data = await state.get_data()
    editing_product_id = data.get("editing_product_id")
    
    if editing_product_id:
        async with async_session() as session:
            product_service = ProductService(session)
            await product_service.update_product(editing_product_id, name=message.text)
            
            await state.clear()
            
            await message.answer(
                Templates.success(f"Product name updated to <b>{message.text}</b>!"),
                parse_mode=ParseMode.HTML,
                reply_markup=product_manage_keyboard(editing_product_id)
            )
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
    editing_product_id = data.get("editing_product_id")
    description = None if message.text == "/skip" else message.text
    
    if editing_product_id:
        async with async_session() as session:
            product_service = ProductService(session)
            await product_service.update_product(editing_product_id, description=description)
            
            await state.clear()
            
            await message.answer(
                Templates.success("Product description updated!"),
                parse_mode=ParseMode.HTML,
                reply_markup=product_manage_keyboard(editing_product_id)
            )
        return
    
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
                new_status = not product.is_active
                await product_service.update_product(product_id, is_active=new_status)
                await callback.answer(f"{'✅ Activated' if new_status else '❌ Deactivated'}")
                
                # Refresh the product detail view with updated status
                product_data = {
                    "name": product.name,
                    "description": product.description,
                    "prices": [{"duration": p.duration, "price": p.price} for p in product.prices]
                }
                text = Templates.product_detail(product_data)
                
                status_emoji = "✅" if new_status else "❌"
                status_text = "Active" if new_status else "Inactive"
                text += f"\n{status_emoji} <b>Status:</b> {status_text}"
                
                await callback.message.edit_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=product_manage_keyboard(product_id, new_status)
                )
                return
    
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
    
    elif action == "edit_desc" and product_id:
        await state.set_state(AdminStates.waiting_product_description)
        await state.update_data(editing_product_id=product_id)
        await callback.message.edit_text(
            Templates.info("Send the new product description (or send /skip to remove):"),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return
    
    elif action == "set_image" and product_id:
        await state.set_state(AdminStates.waiting_product_image)
        await state.update_data(image_product_id=product_id)
        await callback.message.edit_text(
            Templates.info("Send the product image (as a photo):"),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return
    
    elif action == "prices" and product_id:
        await state.update_data(current_product_id=product_id)
        await state.set_state(AdminStates.waiting_price_duration)
        await callback.message.edit_text(
            Templates.info(
                "<b>📋 Send pricing in this format:</b>\n\n"
                "<code>&lt;duration&gt; &lt;credits&gt;</code>\n\n"
                "<b>Examples:</b>\n"
                "<code>1d 1</code> → 1 Day for $1\n"
                "<code>7d 5</code> → 7 Days for $5\n"
                "<code>1m 10</code> → 1 Month for $10\n"
                "<code>3m 25</code> → 3 Months for $25\n\n"
                "<i>Send multiple lines to add multiple prices:</i>\n"
                "<code>1d 1\n3d 2\n7d 5\n30d 10</code>"
            ),
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
                    reply_markup=product_manage_keyboard(product_id, product.is_active)
                )
    
    await callback.answer()


@router.message(AdminStates.waiting_product_image, F.photo)
async def receive_product_image(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    product_id = data.get("image_product_id")
    
    file_id = message.photo[-1].file_id
    
    async with async_session() as session:
        product_service = ProductService(session)
        await product_service.update_product(product_id, image_file_id=file_id)
        
        await state.clear()
        
        await message.answer(
            Templates.success("Product image updated successfully!"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


def parse_duration(duration_str: str) -> tuple:
    """Parse duration string like '1d', '7d', '1m', '3m' to readable format and sort key"""
    import re
    match = re.match(r'^(\d+)(d|m)$', duration_str.lower().strip())
    if not match:
        return None, None, None
    
    num = int(match.group(1))
    unit = match.group(2)
    
    if unit == 'd':
        readable = f"{num} Day{'s' if num > 1 else ''}"
        sort_key = num
    else:
        readable = f"{num} Month{'s' if num > 1 else ''}"
        sort_key = num * 30
    
    return duration_str.lower(), readable, sort_key


@router.message(AdminStates.waiting_price_duration)
async def add_price_duration(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    product_id = data.get("current_product_id")
    
    lines = message.text.strip().split('\n')
    added_prices = []
    errors = []
    
    async with async_session() as session:
        product_service = ProductService(session)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 2:
                errors.append(f"Invalid format: {line}")
                continue
            
            duration_input, price_str = parts
            
            parsed = parse_duration(duration_input)
            if not parsed[0]:
                errors.append(f"Invalid duration: {duration_input}")
                continue
            
            try:
                price = int(price_str)
            except ValueError:
                errors.append(f"Invalid price: {price_str}")
                continue
            
            duration_code, readable_duration, _ = parsed
            
            await product_service.add_price(
                product_id=product_id,
                duration=readable_duration,
                price=price
            )
            added_prices.append(f"✅ {readable_duration} - ${price}")
    
    await state.clear()
    
    if added_prices:
        result_text = "\n".join(added_prices)
        if errors:
            result_text += "\n\n⚠️ <b>Errors:</b>\n" + "\n".join(errors)
        await message.answer(
            Templates.success(f"<b>Prices added:</b>\n\n{result_text}"),
            parse_mode=ParseMode.HTML,
            reply_markup=product_manage_keyboard(product_id)
        )
    else:
        await message.answer(
            Templates.error("No valid prices found!\n\n<b>Format:</b> <code>&lt;duration&gt; &lt;credits&gt;</code>\n\n<b>Examples:</b>\n<code>1d 1</code>\n<code>7d 5</code>\n<code>1m 10</code>\n<code>3m 25</code>"),
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
                "<code>&lt;duration&gt; &lt;key&gt;</code>\n\n"
                "<b>Examples:</b>\n"
                "<code>1d ABC123XYZ</code> → 1 Day\n"
                "<code>7d DEF456UVW</code> → 7 Days\n"
                "<code>1m GHI789RST</code> → 1 Month\n"
                "<code>3m JKL012MNO</code> → 3 Months\n\n"
                "Send multiple lines to add multiple keys.\n\n"
                "<i>Note: Duration must match one of the price options for this product.</i>"
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
    errors = []
    
    async with async_session() as session:
        product_service = ProductService(session)
        
        # Get product prices to validate durations
        product = await product_service.get_product(product_id)
        if not product:
            await message.answer(
                Templates.error("Product not found!"),
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_admin_keyboard()
            )
            await state.clear()
            return
        
        # Create a set of valid durations from product prices
        valid_durations = {p.duration for p in product.prices}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                errors.append(f"Invalid format: {line}")
                continue
            
            duration_code = parts[0].strip()
            key_value = parts[1].strip()
            
            # Parse duration code (e.g., 1d, 7d, 1m, 3m)
            parsed = parse_duration(duration_code)
            if not parsed[0]:
                errors.append(f"Invalid duration: {duration_code}")
                continue
            
            _, readable_duration, _ = parsed
            
            # Check if this duration exists in product prices
            if readable_duration not in valid_durations:
                errors.append(f"Duration '{readable_duration}' not in price list for this product")
                continue
            
            await product_service.add_key(product_id, key_value, readable_duration)
            added += 1
        
        await state.clear()
        
        result_text = f"Added {added} keys successfully!"
        if errors:
            result_text += f"\n\n⚠️ <b>Errors:</b>\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                result_text += f"\n... and {len(errors) - 10} more errors"
        
        await message.answer(
            Templates.success(result_text) if added > 0 else Templates.error(result_text),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )





@router.callback_query(F.data == "admin:admins")
async def manage_admins(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
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
                "first_name": user.first_name if user else None
            })
        
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


@router.callback_query(F.data.startswith("admin:admin:") & ~F.data.contains("add") & ~F.data.contains("remove"))
async def show_admin_detail(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    admin_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        admin_service = AdminService(session)
        user_service = UserService(session)
        admins = await admin_service.get_all_admins()
        admin = next((a for a in admins if a.id == admin_id), None)
        
        if admin:
            # Get user info if available
            user = await user_service.get_user_by_telegram_id(admin.telegram_id)
            
            is_root = admin.telegram_id == config.bot.root_admin_id
            text = f"""
{Templates.DIVIDER}
{'👑' if is_root else '🔑'} <b>ADMIN DETAILS</b>
{Templates.DIVIDER}

🆔 <b>Chat ID:</b> <code>{admin.telegram_id}</code>
👤 <b>Username:</b> @{admin.username or 'N/A'}
📝 <b>Name:</b> {user.first_name if user and user.first_name else 'N/A'}
{'👑 <b>Root Admin</b>' if is_root else ''}
"""
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=admin_manage_keyboard(admin_id, admin.telegram_id, config.bot.root_admin_id)
            )
    await callback.answer()


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
    logger.debug(f"🔧 manage_sellers called by user {callback.from_user.id}")
    
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    try:
        async with async_session() as session:
            seller_service = SellerService(session)
            logger.debug("📝 Fetching sellers from database...")
            sellers = await seller_service.get_all_sellers()
            logger.debug(f"✅ Found {len(sellers)} sellers")
            
            sellers_data = [
                {"id": s.id, "username": s.username, "name": s.name, "is_active": s.is_active}
                for s in sellers
            ]
            
            text = f"""
{Templates.DIVIDER}
⭐ <b>MANAGE TRUSTED SELLERS</b>
{Templates.DIVIDER}

Total sellers: {len(sellers)}

Select a seller to manage:
"""
            
            logger.debug("📝 Editing message with sellers keyboard...")
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=sellers_manage_keyboard(sellers_data)
            )
            logger.debug("✅ Message edited successfully")
        await callback.answer()
    except Exception as e:
        logger.error(f"❌ Error in manage_sellers: {e}")
        await callback.answer(f"Error: {str(e)[:100]}", show_alert=True)


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
    
    data = await state.get_data()
    editing_seller_id = data.get("editing_seller_id")
    username = message.text.replace("@", "").strip()
    
    if editing_seller_id:
        async with async_session() as session:
            seller_service = SellerService(session)
            await seller_service.update_seller(editing_seller_id, username=username)
            
            await state.clear()
            await message.answer(
                Templates.success(f"Seller username updated to @{username}!"),
                parse_mode=ParseMode.HTML,
                reply_markup=seller_manage_keyboard(editing_seller_id)
            )
        return
    
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
    editing_seller_id = data.get("editing_seller_id")
    name = None if message.text == "/skip" else message.text
    
    if editing_seller_id:
        async with async_session() as session:
            seller_service = SellerService(session)
            await seller_service.update_seller(editing_seller_id, name=name)
            
            await state.clear()
            await message.answer(
                Templates.success("Seller name updated!"),
                parse_mode=ParseMode.HTML,
                reply_markup=seller_manage_keyboard(editing_seller_id)
            )
        return
    
    await state.update_data(seller_name=name)
    await state.set_state(AdminStates.waiting_seller_description)
    
    await message.answer(
        Templates.info("Send the seller's <b>description</b> (or /skip):"),
        parse_mode=ParseMode.HTML
    )


@router.message(AdminStates.waiting_seller_description)
async def add_seller_description(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    editing_seller_id = data.get("editing_seller_id")
    description = None if message.text == "/skip" else message.text
    
    if editing_seller_id:
        async with async_session() as session:
            seller_service = SellerService(session)
            await seller_service.update_seller(editing_seller_id, description=description)
            
            await state.clear()
            await message.answer(
                Templates.success("Seller description updated!"),
                parse_mode=ParseMode.HTML,
                reply_markup=seller_manage_keyboard(editing_seller_id)
            )
        return
    
    await state.update_data(seller_description=description)
    await state.set_state(AdminStates.waiting_seller_platforms)
    
    await message.answer(
        Templates.info("Send the seller's <b>platforms</b> (e.g., Telegram: @username, Discord: username#1234) (or /skip):"),
        parse_mode=ParseMode.HTML
    )


@router.message(AdminStates.waiting_seller_platforms)
async def add_seller_platforms(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    editing_seller_id = data.get("editing_seller_id")
    platforms = None if message.text == "/skip" else message.text
    
    if editing_seller_id:
        async with async_session() as session:
            seller_service = SellerService(session)
            await seller_service.update_seller(editing_seller_id, platforms=platforms)
            
            await state.clear()
            await message.answer(
                Templates.success("Seller platforms updated!"),
                parse_mode=ParseMode.HTML,
                reply_markup=seller_manage_keyboard(editing_seller_id)
            )
        return
    
    await state.update_data(seller_platforms=platforms)
    await state.set_state(AdminStates.waiting_seller_country)
    
    await message.answer(
        Templates.info(
            "Send the seller's <b>country</b>:\n\n"
            "<b>Available countries:</b>\n"
            "🇮🇳 India\n"
            "🇵🇰 Pakistan\n"
            "🇧🇩 Bangladesh\n"
            "🇺🇸 USA\n"
            "🇬🇧 UK\n"
            "🇪🇸 Spain\n"
            "🇩🇪 Germany\n"
            "🇫🇷 France\n"
            "🇧🇷 Brazil\n"
            "🇷🇺 Russia\n"
            "🇮🇩 Indonesia\n"
            "🇵🇭 Philippines\n\n"
            "<i>Type the country name or send /skip:</i>"
        ),
        parse_mode=ParseMode.HTML
    )


@router.message(AdminStates.waiting_seller_country)
async def add_seller_country(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    data = await state.get_data()
    editing_seller_id = data.get("editing_seller_id")
    country = None if message.text == "/skip" else message.text.strip()
    
    if editing_seller_id:
        async with async_session() as session:
            seller_service = SellerService(session)
            await seller_service.update_seller(editing_seller_id, country=country)
            
            await state.clear()
            await message.answer(
                Templates.success("Seller country updated!"),
                parse_mode=ParseMode.HTML,
                reply_markup=seller_manage_keyboard(editing_seller_id)
            )
        return
    
    async with async_session() as session:
        seller_service = SellerService(session)
        await seller_service.add_seller(
            username=data["seller_username"],
            name=data.get("seller_name"),
            description=data.get("seller_description"),
            platforms=data.get("seller_platforms"),
            country=country
        )
        
        await state.clear()
        
        await message.answer(
            Templates.success(f"Seller @{data['seller_username']} added!"),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )


@router.callback_query(F.data.startswith("admin:seller:") & ~F.data.contains("add") & ~F.data.contains("remove") & ~F.data.contains("edit") & ~F.data.contains("toggle"))
async def show_seller_detail(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    seller_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        seller_service = SellerService(session)
        sellers = await seller_service.get_all_sellers()
        seller = next((s for s in sellers if s.id == seller_id), None)
        
        if seller:
            status_emoji = "✅" if seller.is_active else "❌"
            status_text = "Active" if seller.is_active else "Inactive"
            
            text = f"""
{Templates.DIVIDER}
⭐ <b>SELLER DETAILS</b>
{Templates.DIVIDER}

👤 <b>Username:</b> @{seller.username}
📝 <b>Name:</b> {seller.name or 'N/A'}
📋 <b>Description:</b> {seller.description or 'N/A'}
🌐 <b>Platforms:</b> {seller.platforms or 'N/A'}
🌍 <b>Country:</b> {seller.country or 'N/A'}
{status_emoji} <b>Status:</b> {status_text}
"""
            try:
                await callback.message.edit_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=seller_manage_keyboard(seller_id, seller.is_active)
                )
            except Exception:
                pass
    await callback.answer()


@router.callback_query(F.data.startswith("admin:seller:toggle:"))
async def toggle_seller(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    seller_id = int(callback.data.split(":")[-1])
    
    async with async_session() as session:
        seller_service = SellerService(session)
        sellers = await seller_service.get_all_sellers()
        seller = next((s for s in sellers if s.id == seller_id), None)
        
        if seller:
            new_status = not seller.is_active
            await seller_service.update_seller(seller_id, is_active=new_status)
            await callback.answer(f"{'✅ Activated' if new_status else '❌ Deactivated'}")
            
            # Refresh the seller detail view
            status_emoji = "✅" if new_status else "❌"
            status_text = "Active" if new_status else "Inactive"
            
            text = f"""
{Templates.DIVIDER}
⭐ <b>SELLER DETAILS</b>
{Templates.DIVIDER}

👤 <b>Username:</b> @{seller.username}
📝 <b>Name:</b> {seller.name or 'N/A'}
📋 <b>Description:</b> {seller.description or 'N/A'}
🌐 <b>Platforms:</b> {seller.platforms or 'N/A'}
🌍 <b>Country:</b> {seller.country or 'N/A'}
{status_emoji} <b>Status:</b> {status_text}
"""
            
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=seller_manage_keyboard(seller_id, new_status)
            )


@router.callback_query(F.data.startswith("admin:seller:edit:"))
async def edit_seller_field(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    parts = callback.data.split(":")
    field = parts[3]
    seller_id = int(parts[4])
    
    await state.update_data(editing_seller_id=seller_id, editing_seller_field=field)
    
    if field == "country":
        await state.set_state(AdminStates.waiting_seller_country)
        from bot.keyboards.admin_kb import country_selection_keyboard
        await callback.message.edit_text(
            Templates.info("Select the new <b>country</b>:"),
            parse_mode=ParseMode.HTML,
            reply_markup=country_selection_keyboard()
        )
        await callback.answer()
        return
    
    field_prompts = {
        "username": "Send the new <b>username</b> (without @):",
        "name": "Send the new <b>display name</b> (or /skip to remove):",
        "description": "Send the new <b>description</b> (or /skip to remove):",
        "platforms": "Send the new <b>platforms</b> (or /skip to remove):"
    }
    
    state_mapping = {
        "username": AdminStates.waiting_seller_username,
        "name": AdminStates.waiting_seller_name,
        "description": AdminStates.waiting_seller_description,
        "platforms": AdminStates.waiting_seller_platforms
    }
    
    await state.set_state(state_mapping[field])
    await callback.message.edit_text(
        Templates.info(field_prompts[field]),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


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





@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "admin:prices")
async def manage_prices(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
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


# =============================================
# BROADCAST HANDLERS
# =============================================

@router.callback_query(F.data == "admin:broadcast")
async def broadcast_menu(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    text = f"""
{Templates.DIVIDER}
📣 <b>BROADCAST MESSAGE</b>
{Templates.DIVIDER}

Send a message to all users of the bot.

Choose the type of broadcast:
"""
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=broadcast_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast:text")
async def broadcast_text_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_broadcast_text)
    
    await callback.message.edit_text(
        Templates.info("Send the <b>text message</b> you want to broadcast to all users:"),
        parse_mode=ParseMode.HTML,
        reply_markup=broadcast_cancel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast:photo")
async def broadcast_photo_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_broadcast_photo)
    
    await callback.message.edit_text(
        Templates.info("Send a <b>photo with caption</b> to broadcast to all users:"),
        parse_mode=ParseMode.HTML,
        reply_markup=broadcast_cancel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast:cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    await state.clear()
    await callback.answer("❌ Broadcast cancelled!")
    callback.data = "admin:back"
    return await admin_back(callback, state)


@router.message(AdminStates.waiting_broadcast_text)
async def process_broadcast_text(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    import asyncio
    
    async with async_session() as session:
        user_service = UserService(session)
        all_users = await user_service.get_all_users()
        
        total = len(all_users)
        sent = 0
        failed = 0
        
        progress_msg = await message.answer(
            Templates.broadcast_progress(total, sent, failed),
            parse_mode=ParseMode.HTML
        )
        
        for i, user in enumerate(all_users):
            try:
                await message.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message.text,
                    parse_mode=ParseMode.HTML
                )
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to send broadcast to {user.telegram_id}: {e}")
                failed += 1
            
            if (i + 1) % 10 == 0 or i == total - 1:
                try:
                    await progress_msg.edit_text(
                        Templates.broadcast_progress(total, sent, failed),
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
            
            await asyncio.sleep(0.05)
        
        await progress_msg.edit_text(
            Templates.broadcast_complete(total, sent, failed),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )
    
    await state.clear()
    logger.info(f"📣 Broadcast completed: {sent}/{total} sent, {failed} failed")


@router.message(AdminStates.waiting_broadcast_photo, F.photo)
async def process_broadcast_photo(message: Message, state: FSMContext):
    if not await is_admin_check(message.from_user.id):
        return
    
    import asyncio
    
    photo_file_id = message.photo[-1].file_id
    caption = message.caption or ""
    
    async with async_session() as session:
        user_service = UserService(session)
        all_users = await user_service.get_all_users()
        
        total = len(all_users)
        sent = 0
        failed = 0
        
        progress_msg = await message.answer(
            Templates.broadcast_progress(total, sent, failed),
            parse_mode=ParseMode.HTML
        )
        
        for i, user in enumerate(all_users):
            try:
                await message.bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=photo_file_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to send broadcast photo to {user.telegram_id}: {e}")
                failed += 1
            
            if (i + 1) % 10 == 0 or i == total - 1:
                try:
                    await progress_msg.edit_text(
                        Templates.broadcast_progress(total, sent, failed),
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
            
            await asyncio.sleep(0.05)
        
        await progress_msg.edit_text(
            Templates.broadcast_complete(total, sent, failed),
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_admin_keyboard()
        )
    
    await state.clear()
    logger.info(f"📣 Photo broadcast completed: {sent}/{total} sent, {failed} failed")


# =============================================
# TOP SELLERS STATISTICS HANDLER
# =============================================

@router.callback_query(F.data == "admin:stats:top_sellers")
async def show_top_sellers(callback: CallbackQuery):
    if not await is_admin_check(callback.from_user.id):
        await callback.answer("⚠️ Access denied!", show_alert=True)
        return
    
    async with async_session() as session:
        order_service = OrderService(session)
        top_sellers = await order_service.get_top_sellers(10)
        
        text = Templates.top_sellers(top_sellers)
        
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=statistics_keyboard()
        )
    await callback.answer()
