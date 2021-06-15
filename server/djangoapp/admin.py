from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel

# Register your models here.

class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

# CarModelInline class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'year')
    list_filter = ['name']
    search_fields = ['name', 'year']
# CarModelAdmin class
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ['name', 'description']
    list_filter = ['name']
    search_fields = ['name']
# CarMakeAdmin class with CarModelInline

# Register models here

admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
