from django.core.management.base import BaseCommand
from recs.lightfm_pipeline import train_and_save
class Command(BaseCommand):
    help='Train LightFM if available; else fallback'
    def add_arguments(self, parser): parser.add_argument('--epochs', type=int, default=8)
    def handle(self, *a, **kw):
        p=train_and_save(epochs=kw['epochs']); self.stdout.write(self.style.SUCCESS(f'Saved model to {p}'))
