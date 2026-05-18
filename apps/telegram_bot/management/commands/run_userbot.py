"""
Management command to run Telegram userbots.

Run a specific account:
    python manage.py run_userbot --phone +1234567890

Run all active accounts (in separate threads):
    python manage.py run_userbot --all
"""
import threading
import logging
from django.core.management.base import BaseCommand
from apps.telegram_bot.models import TelegramAccount
from apps.telegram_bot.services.userbot_service import UserbotService

logger = logging.getLogger("apps.telegram_bot")


class Command(BaseCommand):
    help = "Run Telegram userbot(s)."

    def add_arguments(self, parser):
        parser.add_argument("--phone", type=str, help="Phone number of specific account")
        parser.add_argument("--all", action="store_true", help="Run all active accounts")

    def handle(self, *args, **options):
        if options["all"]:
            accounts = TelegramAccount.objects.filter(status=TelegramAccount.Status.ACTIVE)
            if not accounts.exists():
                self.stdout.write(self.style.WARNING("No active Telegram accounts found."))
                return

            threads = []
            for account in accounts:
                self.stdout.write(f"Starting userbot for {account.phone_number}...")
                t = threading.Thread(
                    target=self._run_account,
                    args=(account,),
                    daemon=True,
                    name=f"userbot-{account.phone_number}",
                )
                t.start()
                threads.append(t)

            self.stdout.write(self.style.SUCCESS(f"Started {len(threads)} userbot(s)."))
            for t in threads:
                t.join()

        elif options["phone"]:
            try:
                account = TelegramAccount.objects.get(phone_number=options["phone"])
                self.stdout.write(f"Starting userbot for {account.phone_number}...")
                self._run_account(account)
            except TelegramAccount.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Account {options['phone']} not found."))
        else:
            self.stdout.write(self.style.ERROR("Provide --phone or --all"))

    def _run_account(self, account: TelegramAccount):
        try:
            service = UserbotService(account)
            service.run()
        except Exception as e:
            logger.error("Userbot error [%s]: %s", account.phone_number, e)
