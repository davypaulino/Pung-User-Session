import asyncio

from worker.listeners.orchestrator_listerner import OrchestratorListener
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run <game_integration> to start the game integration worker."

    async def orchetrator(self):
        game_sync_listener = OrchestratorListener()

        try:
            await game_sync_listener.listen()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("All tasks have been completed."))
        except asyncio.CancelledError:
            self.stdout.write(self.style.WARNING("Worker has been stopped."))

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting game integration worker..."))
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.orchetrator())
            loop.run_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Worker has been stopped."))
            loop.stop()