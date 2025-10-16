from django.core.management.base import BaseCommand
from courses.models import ModuleProgress, LessonProgress


class Command(BaseCommand):
    help = 'Sync completion_percentage with progress_percentage for existing records'

    def handle(self, *args, **options):
        self.stdout.write('Syncing completion_percentage fields...')
        
        # Update ModuleProgress records
        module_progress_count = 0
        for progress in ModuleProgress.objects.all():
            if progress.progress_percentage != progress.completion_percentage:
                progress.completion_percentage = progress.progress_percentage
                progress.save()
                module_progress_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated {module_progress_count} ModuleProgress records'
            )
        )
        
        # LessonProgress already has completion_percentage, so just ensure it's calculated
        lesson_progress_count = 0
        for progress in LessonProgress.objects.all():
            if progress.completion_percentage == 0 and not progress.is_completed:
                # Recalculate progress
                progress.calculate_progress()
                lesson_progress_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Recalculated {lesson_progress_count} LessonProgress records'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully synced completion_percentage fields!')
        )
