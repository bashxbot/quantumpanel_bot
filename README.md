# 🚀 Quantum Panel Bot

A lightning-fast and premium Telegram panel bot with User and Admin ecosystems.

## Features

### 👤 User Features
- Beautiful dashboard with profile info, balance, and status
- Trusted sellers list
- Products catalog (Free/Premium access)
- Order history
- Balance management
- Premium upgrade system

### 👑 Admin Features
- Product management (add/edit/delete with images)
- Price list management per product
- Reseller management
- Key/stock management with auto-assignment
- Credits management
- Admin management (with root admin protection)
- Statistics dashboard

## Tech Stack

| Feature    | Library              |
| ---------- | -------------------- |
| Bot engine | **Aiogram v3**       |
| Database   | **PostgreSQL**       |
| ORM        | **SQLAlchemy Async** |
| Migrations | **Alembic**          |
| Caching    | **Redis + aioredis** |
| Images     | **Pillow**           |
| Config     | **python-dotenv**    |
| Logs       | **Loguru**           |

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `BOT_TOKEN` - Your Telegram bot token from @BotFather
- `ROOT_ADMIN_ID` - Your Telegram user ID (will be the root admin)
- `ADMIN_USERNAME` - Admin username for contact messages
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (optional)

### 2. Database Setup

The database tables are created automatically on first run.

For migrations:
```bash
cd bot
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 3. Run the Bot

```bash
python run.py
```

Or:
```bash
python -m bot.main
```

## Project Structure

```
bot/
├── __init__.py
├── config.py           # Configuration management
├── database.py         # Database connection
├── main.py            # Bot entry point
├── handlers/          # Message/callback handlers
│   ├── user.py        # User commands & callbacks
│   └── admin.py       # Admin commands & callbacks
├── models/            # SQLAlchemy models
│   ├── user.py
│   ├── admin.py
│   ├── product.py
│   ├── key.py
│   ├── order.py
│   └── seller.py
├── services/          # Business logic
│   ├── user_service.py
│   ├── admin_service.py
│   ├── product_service.py
│   ├── order_service.py
│   ├── seller_service.py
│   └── cache.py
├── keyboards/         # Inline keyboards
│   ├── user_kb.py
│   └── admin_kb.py
├── templates/         # Message templates
│   └── messages.py
├── middlewares/       # Bot middlewares
│   └── database.py
└── alembic/          # Database migrations
    └── versions/
```

## Commands

### User Commands
- `/start` - Show main dashboard

### Admin Commands
- `/admin` - Open admin panel

## License

MIT
