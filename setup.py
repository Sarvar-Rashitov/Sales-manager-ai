"""
Quick setup script — run once after cloning.
Usage: python setup.py
"""
import os
import subprocess
import sys
import shutil


def run(cmd):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  ✗ Command failed: {cmd}")
        sys.exit(1)


def main():
    print("\n🤖 AI Sales Manager — Setup\n")

    # Copy .env
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("  ✓ Created .env from .env.example")
        print("  ⚠  Edit .env and add your OPENAI_API_KEY and TELEGRAM credentials\n")
    else:
        print("  ✓ .env already exists")

    # Create media directories
    for d in ["media/telegram_sessions", "media/faiss_indexes", "media/knowledge_base"]:
        os.makedirs(d, exist_ok=True)
    print("  ✓ Created media directories")

    # Run migrations
    print("\nRunning migrations...")
    run("python manage.py migrate")

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("  1. Edit .env with your API keys")
    print("  2. python manage.py createsuperuser")
    print("  3. python manage.py runserver")
    print("  4. Visit http://localhost:8000")
    print("\nBackground tasks:")
    print("  python manage.py process_followups --loop")
    print("\nTelegram userbot:")
    print("  python manage.py run_userbot --all")


if __name__ == "__main__":
    main()
