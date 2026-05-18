# Local Development Setup Guide

## Prerequisites
- Python 3.11+
- pip

## Quick Start (5 minutes)

### 1. Clone and enter the project
```bash
cd ai_sales_manager
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements/local.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and TELEGRAM credentials
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Start the development server
```bash
# Standard HTTP server
python manage.py runserver

# OR with WebSocket support (Django Channels)
daphne config.asgi:application
```

Visit: http://localhost:8000

Admin panel: http://localhost:8000/admin/

---

## Running Background Tasks (No Celery)

### Process follow-ups (run once)
```bash
python manage.py process_followups
```

### Process follow-ups (continuous loop, every 5 min)
```bash
python manage.py process_followups --loop
```

### Add to crontab (Linux/Mac)
```bash
# Every 5 minutes
*/5 * * * * cd /path/to/ai_sales_manager && venv/bin/python manage.py process_followups
```

### Windows Task Scheduler
Create a task that runs every 5 minutes:
```
python C:\path\to\ai_sales_manager\manage.py process_followups
```

---

## Running Telegram Userbot

### Add a Telegram account first
1. Go to http://localhost:8000/telegram/accounts/add/
2. Enter your phone number
3. Enter the OTP code sent to your Telegram
4. If 2FA is enabled, enter your password

### Start the userbot
```bash
# Single account
python manage.py run_userbot --phone +1234567890

# All active accounts
python manage.py run_userbot --all
```

---

## Getting Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application
4. Copy `api_id` and `api_hash` to your `.env` file

---

## Getting OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to `.env` as `OPENAI_API_KEY`

---

## Project Structure

```
ai_sales_manager/
├── manage.py
├── .env.example          ← Copy to .env
├── config/
│   ├── settings/
│   │   ├── base.py       ← Shared settings
│   │   ├── local.py      ← SQLite3, debug on
│   │   └── production.py ← PostgreSQL, secure
│   ├── urls.py           ← Root URL config
│   └── asgi.py           ← WebSocket support
├── apps/
│   ├── accounts/         ← Auth, users, orgs
│   ├── crm/              ← Leads, contacts, deals
│   ├── ai_agents/        ← AI agent system
│   ├── telegram_bot/     ← Telethon userbot
│   ├── knowledge_base/   ← RAG / FAISS
│   ├── followups/        ← Follow-up scheduler
│   ├── messaging/        ← WebSocket chat
│   ├── analytics/        ← Stats & charts
│   ├── dashboard/        ← Main dashboard
│   ├── sales/            ← Proposals
│   └── common/           ← Shared utilities
├── templates/            ← Django templates
├── static/               ← CSS, JS, images
├── media/                ← Uploads, FAISS indexes
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

---

## Architecture Overview

```
Browser (HTMX + Alpine.js + TailwindCSS)
         ↓
Django Views (MVT)
         ↓
Services Layer (business logic)
         ↓
AI Agents (OpenAI + LangChain + RAG)
         ↓
Django ORM
         ↓
SQLite3 (local) / PostgreSQL (production)
```

---

## AI Agent Routing

Messages are routed to agents based on lead status:

| Lead Status   | Agent               |
|---------------|---------------------|
| new           | ReceptionAgent      |
| contacted     | QualificationAgent  |
| qualified     | SalesAgent          |
| demo          | SalesAgent          |
| negotiation   | SalesAgent          |
| lost          | FollowUpAgent       |

---

## Production Deployment

### Switch to PostgreSQL
```bash
# Set DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=config.settings.production

# Set all required env vars (see .env.example)
python manage.py migrate
python manage.py collectstatic
gunicorn config.wsgi:application
```

### With WebSockets
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```
