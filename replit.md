# Quantum Panel Bot

## Overview

Quantum Panel Bot is a premium Telegram bot built with Python for managing a digital products marketplace. The bot features a dual-ecosystem architecture with separate User and Admin interfaces. Users can browse products, make purchases, manage their balance, and upgrade to premium status. Admins have comprehensive tools for managing products, prices, keys/stock, resellers, credits, and other administrators. The system is designed for high performance with async operations throughout and includes caching for frequently accessed data.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework Architecture
- **Framework**: Aiogram v3 (async Telegram bot framework)
- **Message Routing**: Router-based handler organization separating user and admin flows
- **State Management**: FSM (Finite State Machine) for multi-step admin workflows using MemoryStorage
- **Middleware**: Custom database middleware to inject AsyncSession into handlers automatically

**Rationale**: Aiogram v3 provides native async/await support and clean separation of concerns through routers, essential for handling concurrent user requests efficiently.

### Database Architecture
- **ORM**: SQLAlchemy 2.0+ with async extensions (AsyncSession)
- **Connection Pool**: NullPool to prevent connection issues in serverless/container environments
- **Migrations**: Alembic for schema version control
- **Models**: Seven core entities with relationships:
  - User (balance, premium status, reseller flag)
  - Admin (with root admin protection)
  - Product (with image support)
  - ProductPrice (multiple durations per product)
  - ProductKey (stock management with auto-assignment)
  - Order (purchase history)
  - TrustedSeller (verified sellers list)

**Design Decisions**:
- NullPool chosen over standard pooling to avoid connection lifecycle issues in ephemeral environments
- Lazy loading configured as "selectin" to avoid N+1 query problems while maintaining async compatibility
- TimestampMixin provides automatic created_at/updated_at tracking across all entities

### Caching Layer
- **Technology**: Redis with aioredis client
- **Strategy**: Cache-aside pattern with TTL-based expiration
- **Cached Data**: User lookups, admin checks, product lists, seller lists
- **Invalidation**: Pattern-based invalidation on writes (e.g., `cache.invalidate_pattern("products:*")`)
- **Graceful Degradation**: System continues functioning if Redis is unavailable

**Rationale**: Reduces database load for frequently accessed data like admin authorization checks and product catalogs. Graceful degradation ensures the bot remains operational during cache failures.

### Service Layer Pattern
- **Services**: Dedicated service classes for each domain (UserService, AdminService, ProductService, etc.)
- **Responsibilities**: Business logic, data access, cache management
- **Session Management**: Each service receives an AsyncSession, enabling transaction control at the handler level

**Benefits**: 
- Clear separation between HTTP/Telegram layer and business logic
- Easier testing and maintenance
- Consistent data access patterns

### Authorization System
- **Root Admin**: Single immutable admin defined via environment variable (ROOT_ADMIN_ID)
- **Admin Hierarchy**: Root admin can add/remove other admins but cannot be removed
- **Caching**: Admin status cached for 10 minutes to reduce database hits
- **Protection**: Built-in safeguards prevent root admin deletion or demotion

### User Access Control
- **Free vs Premium**: Two-tier user system with premium gating for product access
- **Reseller Flag**: Separate boolean for reseller permissions
- **Balance System**: Floating-point balance for credit-based purchases

### Product & Pricing System
- **Flexible Pricing**: Each product supports multiple duration-based price points (e.g., 1-month, 3-month, lifetime)
- **Stock Management**: ProductKey entities with is_used flag for inventory tracking
- **Auto-Assignment**: Keys automatically assigned to orders upon purchase
- **Image Support**: Products store Telegram file_id for image caching

### Template System
- **Message Templates**: Centralized Templates class for consistent formatting
- **Rich Formatting**: Uses Telegram HTML parsing with emoji and Unicode box-drawing characters
- **Reusability**: Shared templates across user and admin flows

### Logging Strategy
- **Library**: Loguru for structured, colorized logging
- **Dual Output**: Console (INFO+) and file-based (DEBUG+) logging
- **Rotation**: Daily log rotation with 7-day retention
- **Context**: Logs include function/line numbers for debugging

## External Dependencies

### Required Services
1. **PostgreSQL Database**
   - Primary data store
   - Connection via DATABASE_URL environment variable
   - Automatically converted to asyncpg driver URL

2. **Redis Cache** (optional but recommended)
   - Performance optimization layer
   - Connection via REDIS_URL (defaults to localhost:6379)
   - System operates without Redis if unavailable

3. **Telegram Bot API**
   - Core communication platform
   - Requires BOT_TOKEN from @BotFather
   - Uses Aiogram v3 client with default polling

### Python Dependencies
- **aiogram**: Telegram bot framework (v3.x)
- **sqlalchemy**: Async ORM (v2.0+)
- **alembic**: Database migrations
- **redis/aioredis**: Async Redis client
- **python-dotenv**: Environment configuration
- **loguru**: Advanced logging
- **Pillow**: Image processing (for future image generation features)
- **asyncpg**: PostgreSQL async driver (via SQLAlchemy)

### Environment Configuration
Required variables in `.env`:
- `BOT_TOKEN`: Telegram bot authentication token
- `ROOT_ADMIN_ID`: Telegram user ID for root administrator
- `ADMIN_USERNAME`: Contact username for support messages
- `DATABASE_URL`: PostgreSQL connection string (postgres:// or postgresql://)
- `REDIS_URL`: Redis connection string (optional, defaults to localhost)

### Deployment Considerations
- Designed for containerized deployment (Docker/Kubernetes)
- NullPool prevents connection issues in ephemeral containers
- Graceful Redis degradation supports environments without caching
- Environment-based configuration for 12-factor app compliance