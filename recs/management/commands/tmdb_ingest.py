# recs/management/commands/tmdb_ingest.py
from django.core.management.base import BaseCommand
from time import sleep
from recs.tmdb import discover, detail, IMG, get_genres
from core.models import Movie

class Command(BaseCommand):
    help = "Ingest TMDB popular movies into local DB"

    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=3)
        parser.add_argument('--sleep', type=float, default=0.5)  # polite delay

    def handle(self, *a, **kw):
        pages = kw['pages']; delay = kw['sleep']
        count = 0
        for p in range(1, pages + 1):
            try:
                results = discover(page=p)
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"[page {p}] discover failed: {e} — skipping"))
                continue

            for m in results:
                mid = m.get('id')
                try:
                    det = detail(mid)
                except Exception as e:
                    self.stderr.write(self.style.WARNING(f"detail({mid}) failed: {e} — skipping"))
                    continue

                Movie.objects.update_or_create(
                    tmdb_id=mid,
                    defaults=dict(
                        title=det.get('title') or '',
                        overview=det.get('overview') or '',
                        year=(det.get('release_date') or '')[:4],
                        poster=(IMG + det['poster_path']) if det.get('poster_path') else '',
                        popularity=det.get('popularity') or 0.0,
                        vote=det.get('vote_average') or 0.0,
                    )
                )
                count += 1
                if delay: sleep(delay)

        self.stdout.write(self.style.SUCCESS(f"Ingested/updated {count} movies."))
