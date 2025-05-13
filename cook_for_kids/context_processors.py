from .models import GlobalSettings

def global_settings(request):
    settings = GlobalSettings.get_current()

    # Map month number to month name
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']

    try:
        month_index = int(settings.month) - 1  # Convert to 0-based index
        if 0 <= month_index < 12:
            month_name = month_names[month_index]
        else:
            month_name = "Unknown"
    except (ValueError, TypeError):
        month_name = "Unknown"

    return {
        'global_year': settings.year,
        'global_month': settings.month,
        'global_month_name': month_name
    }
