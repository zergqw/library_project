from django.contrib import admin

from .models import Loan


class LoanStatusFilter(admin.SimpleListFilter):
    title = 'состояние'
    parameter_name = 'loan_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'На руках'),
            ('returned', 'Возвращены'),
            ('overdue', 'Просрочены'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'active':
            return queryset.filter(actual_return_date__isnull=True)
        if value == 'returned':
            return queryset.filter(actual_return_date__isnull=False)
        if value == 'overdue':
            overdue_ids = [loan.pk for loan in queryset if loan.is_overdue]
            return queryset.filter(pk__in=overdue_ids)
        return queryset


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book_instance', 'reader', 'loan_date', 'return_date', 'actual_return_date')
    list_filter = (LoanStatusFilter, 'loan_date', 'return_date')
    search_fields = ('book_instance__book__title', 'reader__user__last_name', 'reader__ticket_number')
