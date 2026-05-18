"""
Management command to process due follow-ups.

Run manually:
    python manage.py process_followups

Or add to crontab (every 5 minutes):
    */5 * * * * cd /path/to/project && python manage.py process_followups

Or run as a loop (for local dev):
    python manage.py process_followups --loop
"""
import time
import logging
from django.core.management.base import BaseCommand
from apps.followups.services import FollowUpService

logger = logging.getLogger("apps.followups")


class Command(BaseCommand):
    help = "Process all pending follow-ups that are due."

    def add_arguments(self, parser):
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Run continuously (check every 5 minutes)",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=300,
            help="Loop interval in seconds (default: 300)",
        )

    def handle(self, *args, **options):
        if options["loop"]:
            self.stdout.write("Starting follow-up processor loop...")
            while True:
                self._run_once()
                time.sleep(options["interval"])
        else:
            self._run_once()

    def _run_once(self):
        due = FollowUpService.get_due_followups()
        count = due.count()
        self.stdout.write(f"Found {count} due follow-ups.")

        success = 0
        for followup in due:
            if FollowUpService.execute_followup(followup):
                success += 1

        self.stdout.write(self.style.SUCCESS(f"Processed {success}/{count} follow-ups."))

        # Also schedule abandoned lead follow-ups
        scheduled = FollowUpService.schedule_abandoned_lead_followups(days_inactive=3)
        if scheduled:
            self.stdout.write(f"Scheduled {scheduled} abandoned lead follow-ups.")
