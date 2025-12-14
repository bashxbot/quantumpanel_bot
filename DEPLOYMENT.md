# Deployment Guide for Render

This guide explains how to deploy the Quantum Panel bot on Render.

## Prerequisites

- A Render account (https://render.com)
- A PostgreSQL database (can be created on Render)
- Redis instance (optional, for caching - can use Render Redis or external like Upstash)
- Telegram Bot Token from @BotFather

## Environment Variables

Set these environment variables in Render:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token | `123456:ABC-DEF...` |
| `ROOT_ADMIN_ID` | Your Telegram user ID | `123456789` |
| `ADMIN_USERNAME` | Admin contact username | `@YourAdminUsername` |
| `MANAGER_USERNAME` | Manager contact username | `@YourManagerUsername` |
| `REPORT_CHANNEL` | Channel for purchase reports | `@YourChannel` or chat ID |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `REDIS_URL` | (Optional) Redis connection string | `redis://...` or `rediss://...` |

## Build Command

```bash
cd client && npm install && npm run build && cd .. && pip install -r requirements.txt
```

## Start Command

```bash
python web_server.py
```

## Python Dependencies (requirements.txt)

The following Python packages are required:
- aiohttp>=3.13.2
- aiogram>=3.16.0
- loguru>=0.7.3
- python-dotenv>=1.0.0
- sqlalchemy[asyncio]>=2.0.0
- asyncpg>=0.29.0
- redis>=5.0.0
- pillow>=10.0.0
- gunicorn>=21.0.0

## Node.js Dependencies

The React frontend requires:
- react, react-dom, react-router-dom
- tailwindcss, @tailwindcss/vite
- vite, typescript

Install with: `cd client && npm install`

## Deployment Steps on Render

1. **Create a Web Service**
   - Go to Render Dashboard > New > Web Service
   - Connect your GitHub/GitLab repository
   - Select "Python 3" as the environment

2. **Configure the Service**
   - **Build Command**: `cd client && npm install && npm run build && cd .. && pip install -r requirements.txt`
   - **Start Command**: `python web_server.py`
   - **Instance Type**: Choose based on your needs (Starter works for small bots)

3. **Add Environment Variables**
   - Add all the environment variables listed above

4. **Create a PostgreSQL Database** (if needed)
   - Go to Render Dashboard > New > PostgreSQL
   - Copy the Internal Database URL
   - Add as `DATABASE_URL` in your web service

5. **Optional: Add Redis**
   - Create a Redis instance on Render or use Upstash
   - Add the connection URL as `REDIS_URL`

6. **Deploy**
   - Click "Create Web Service"
   - Wait for the build to complete

## Important Notes

- The web server runs on port 5000 by default
- The React admin panel is built during deployment and served by the Python server
- The database tables are created automatically on first run

## Database Migration for Decimal Prices

If your prices or balances show $0.00 instead of decimal values (e.g., $0.25), you need to run the migration script. This converts INTEGER columns to NUMERIC type to support decimals.

**Run the migration on Render:**
1. Go to your Render service
2. Open the Shell tab
3. Run: `python -m bot.migrate_prices`

This will update both `product_prices.price` and `users.balance` columns to support decimal values.

**Note:** After migration, you may need to re-add prices if they were stored as integers (e.g., $0.25 stored as $0).

## Troubleshooting

- **Bot not responding**: Check that `BOT_TOKEN` is correct and the bot is started
- **Database errors**: Ensure `DATABASE_URL` uses `postgres://` or `postgresql://` format
- **Admin panel not loading**: Make sure the build command completed successfully
- **Redis errors**: Redis is optional; the bot works without it

## Local Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and build frontend
cd client && npm install && npm run build && cd ..

# Run the server
python web_server.py
```
