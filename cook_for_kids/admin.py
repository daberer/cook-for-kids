from django.contrib import admin
from .models import Kid, Dish, Holiday, Waiverday, GlobalSettings

@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_dishes', 'exempt')
    list_filter = ('exempt',)
    ordering = ('name',)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('year', 'month', 'excursion_day_name', 'weekly_event_text', 'last_updated')
    list_filter = ('year', 'month', 'excursion_day')
    fields = (
        ('year', 'month'),
        'excursion_day',
        'weekly_event_text',
        'last_updated'
    )
    readonly_fields = ('last_updated',)

    def excursion_day_name(self, obj):
        return obj.excursion_day_name
    excursion_day_name.short_description = 'Excursion Day'

@admin.register(Waiverday)
class WaiverdayAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_waived_kids', 'get_non_waived_kids')
    list_filter = ('date',)
    date_hierarchy = 'date'

    def get_waived_kids(self, obj):
        return ", ".join([kid.name for kid in obj.kid.all()])

    def get_non_waived_kids(self, obj):
        # Get all kids who are not exempt and not in this waiverday
        waived_kids = obj.kid.all()
        non_waived = Kid.objects.filter(exempt=False).exclude(id__in=[k.id for k in waived_kids])
        return ", ".join([kid.name for kid in non_waived])

    get_waived_kids.short_description = 'Waived Kids'
    get_non_waived_kids.short_description = 'Non-Waived Kids'

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'text')
    list_filter = ('date',)
    date_hierarchy = 'date'  # Adds date navigation at the top
    ordering = ('-date',)    # Orders by date descending (newest first)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('__str__', 'cook')  # Add any other fields you want to display

    # Optional: Add a filter by cook in the right sidebar
    list_filter = ('cook',)

    # Optional: Add search functionality
    search_fields = ('cook__name',)  # Assuming Kid has a name field