
from aiohttp import web
import asyncio
import os
from bot.main import main as bot_main
from loguru import logger

async def index_page(request):
    """Serve the HTML landing page"""
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    return web.FileResponse(html_path)

async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="Bot is running", status=200)

async def start_web_server():
    """Start web server on port 5000"""
    app = web.Application()
    app.router.add_get('/', index_page)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    logger.info("🌐 Web server started on http://0.0.0.0:5000")

async def main():
    """Run both web server and bot concurrently"""
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
