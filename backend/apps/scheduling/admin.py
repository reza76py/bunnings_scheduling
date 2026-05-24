from django.contrib import admin
from .models import Supplier, CountingSession, SessionParticipant


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'created_at']


class SessionParticipantInline(admin.TabularInline):
	model = SessionParticipant
	extra = 0
	readonly_fields = ['name', 'joined_at', 'left_at']
	can_delete = False


@admin.register(CountingSession)
class CountingSessionAdmin(admin.ModelAdmin):
	inlines = [SessionParticipantInline]
	list_display = ['id', 'supplier', 'store_number', 'value', 'people_working', 'start_time', 'end_time', 'duration_minutes', 'created_at']
	list_filter = ['supplier', 'created_at']
	search_fields = ['supplier__name', 'people_working']

	@admin.display(description='store_number')
	def store_number(self, obj):
		# Expect frontend format: "Store <number> | person1, person2"
		if not obj.people_working:
			return ''

		parts = obj.people_working.split('|', 1)
		store_part = parts[0].strip()
		if store_part.lower().startswith('store '):
			return store_part[6:].strip()
		return ''
