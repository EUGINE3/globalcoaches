# Progress Tracking Implementation

## Overview

This document describes the comprehensive progress tracking implementation for the Global Coaches Academy. The system tracks student progress through modules, lessons, and resources, providing consistent progress display across all templates.

## Template Snippet

The core template snippet for displaying progress is:

```django
Progress: {{ item.completion_percentage|default:0|floatformat:0 }}%
```

This snippet:
- Gets the `completion_percentage` from an item object
- Defaults to 0 if the value is not available or is null
- Formats as a float with 0 decimal places (removes decimal places)
- Displays as a percentage with the `%` symbol

## Implementation Components

### 1. Models

#### ModuleProgress Model
- **Fields**: `progress_percentage`, `completion_percentage` (alias for template compatibility)
- **Purpose**: Tracks overall module progress for students
- **Auto-sync**: `completion_percentage` is automatically synced with `progress_percentage` on save

#### LessonProgress Model
- **Fields**: `completion_percentage`
- **Purpose**: Tracks individual lesson completion
- **Calculation**: Based on required resources and assignments completed

### 2. Progress Calculator (`progress_utils.py`)

The `ProgressCalculator` class provides centralized progress calculation:

```python
# Calculate lesson progress
completion = ProgressCalculator.calculate_lesson_progress(student, lesson)

# Calculate topic progress
completion = ProgressCalculator.calculate_topic_progress(student, topic)

# Calculate module progress
completion = ProgressCalculator.calculate_module_progress(student, program_module)

# Update progress records
ProgressCalculator.update_lesson_progress(student, lesson)
ProgressCalculator.update_module_progress(student, program_module)
```

### 3. Template Tags (`progress_tags.py`)

Custom template tags for consistent progress display:

```django
{% load progress_tags %}

<!-- Progress bar -->
{% progress_bar item.completion_percentage %}

<!-- Progress circle -->
{% progress_circle item.completion_percentage %}

<!-- Filters -->
{{ item.completion_percentage|progress_display_class }}
{{ item.completion_percentage|progress_color }}
{{ item.completion_percentage|format_progress }}
```

### 4. Progress Display Helper

The `ProgressDisplayHelper` class provides utility methods:

- `get_progress_display_class(percentage)`: Returns CSS class based on progress
- `get_progress_color(percentage)`: Returns color based on progress
- `format_progress_percentage(percentage, decimal_places)`: Formats percentage for display

## Progress Calculation Logic

### Lesson Progress
Calculated based on:
- Required resources completed
- Assignments completed with passing grade (≥70%)

### Topic Progress
Calculated based on:
- Lessons completed within the topic
- Topic-level assignments completed

### Module Progress
Calculated based on:
- Average progress across all topics in the module
- Module-level assignments completed

## Usage Examples

### In Templates

```django
<!-- Basic progress display -->
Progress: {{ item.completion_percentage|default:0|floatformat:0 }}%

<!-- Using template tags -->
{% progress_bar item.completion_percentage %}

<!-- With custom styling -->
<div class="progress-bar">
    <div class="progress-fill" 
         style="width: {{ item.completion_percentage|default:0 }}%; 
                background-color: {{ item.completion_percentage|progress_color }};">
    </div>
</div>
```

### In Views

```python
from courses.progress_utils import ProgressCalculator

# Update lesson progress
lesson_progress = ProgressCalculator.update_lesson_progress(student, lesson)

# Update module progress
module_progress = ProgressCalculator.update_module_progress(student, program_module)

# Recalculate all progress
result = ProgressCalculator.recalculate_all_progress(student, program_level)
```

## Database Migration

The implementation includes a migration that:
1. Adds the `completion_percentage` field to `ModuleProgress`
2. Syncs existing records to populate the new field

Run the migration:
```bash
python manage.py migrate
python manage.py sync_completion_percentage
```

## Management Commands

### sync_completion_percentage
Syncs `completion_percentage` with `progress_percentage` for existing records:

```bash
python manage.py sync_completion_percentage
```

## Testing

The implementation includes comprehensive tests in `test_progress_implementation.py`:

```bash
python manage.py shell -c "
from courses.test_progress_implementation import test_progress_implementation
test_progress_implementation()
"
```

## CSS Classes

The progress display system uses the following CSS classes:

- `progress-complete`: 100% completion (green)
- `progress-high`: 75-99% completion (teal)
- `progress-medium`: 50-74% completion (blue)
- `progress-low`: 25-49% completion (yellow)
- `progress-minimal`: 0-24% completion (red)

## Color Scheme

Progress colors are dynamically assigned based on completion percentage:

- **0-24%**: `#dc3545` (Danger red)
- **25-49%**: `#ffc107` (Warning yellow)
- **50-74%**: `#17a2b8` (Info blue)
- **75-99%**: `#20c997` (Teal)
- **100%**: `#28a745` (Success green)

## Integration Points

The progress system integrates with:

1. **Views**: Automatic progress calculation when accessing lessons/modules
2. **Templates**: Consistent progress display across all pages
3. **Models**: Automatic sync between `progress_percentage` and `completion_percentage`
4. **Admin**: Progress tracking in Django admin interface
5. **API**: Progress data available for mobile/API consumption

## Best Practices

1. **Always use the template snippet**: `{{ item.completion_percentage|default:0|floatformat:0 }}%`
2. **Use ProgressCalculator**: For all progress calculations in views
3. **Template tags**: Use `{% progress_bar %}` for consistent styling
4. **Default values**: Always provide defaults for progress percentages
5. **Recalculation**: Run recalculation after major data changes

## Troubleshooting

### Common Issues

1. **Progress not updating**: Ensure `ProgressCalculator.update_*_progress()` is called
2. **Template errors**: Check that `completion_percentage` field exists
3. **Inconsistent display**: Use the provided template tags
4. **Migration issues**: Run `sync_completion_percentage` command

### Debug Commands

```bash
# Check progress records
python manage.py shell -c "
from courses.models import ModuleProgress, LessonProgress
print('ModuleProgress records:', ModuleProgress.objects.count())
print('LessonProgress records:', LessonProgress.objects.count())
"

# Recalculate all progress
python manage.py shell -c "
from courses.progress_utils import ProgressCalculator
from django.contrib.auth.models import User
user = User.objects.first()
result = ProgressCalculator.recalculate_all_progress(user)
print('Recalculation result:', result)
"
```

## Future Enhancements

1. **Real-time updates**: WebSocket integration for live progress updates
2. **Progress analytics**: Detailed progress reporting and analytics
3. **Gamification**: Progress badges and achievements
4. **Mobile API**: RESTful API for mobile app integration
5. **Progress notifications**: Email/SMS notifications for progress milestones
