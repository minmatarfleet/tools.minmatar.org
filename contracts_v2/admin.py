from django.contrib import admin
from .models import EveContractEntity, EveDoctrineExpectation, EveContractExpectation, EveContractLocation, EveContractTaxReport

# Register your models here.
@admin.register(EveContractExpectation)
class EveContractExpectationAdmin(admin.ModelAdmin):
    list_display = ('fitting', 'location')
    list_filter = ('location', 'entities')

@admin.register(EveContractEntity)
class EveContractEntityAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'type', 'expectations_count')
    list_filter = ('type',)

    @admin.display(empty_value='???')
    def expectations_count(self, obj):
        return len(obj.expectations.all())

admin.site.register(EveContractLocation)
admin.site.register(EveContractTaxReport)
admin.site.register(EveDoctrineExpectation)