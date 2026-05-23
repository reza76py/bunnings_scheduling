from django.contrib import admin
from .models import Supplier, CountingSession


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'created_at']


@admin.register(CountingSession)
class CountingSessionAdmin(admin.ModelAdmin):
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
