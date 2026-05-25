from io import BytesIO
import zoneinfo

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook

from .models import Supplier, CountingSession, SessionParticipant


brisbane = zoneinfo.ZoneInfo('Australia/Brisbane')
utc = zoneinfo.ZoneInfo('UTC')


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
	actions = ['export_as_excel']
	inlines = [SessionParticipantInline]
	list_display = ['id', 'supplier', 'store_number', 'value', 'people_working', 'start_time', 'end_time', 'duration_minutes', 'created_at']
	list_filter = ['supplier', 'created_at']
	search_fields = ['supplier__name', 'people_working']

	@admin.action(description='Export selected sessions to Excel')
	def export_as_excel(self, request, queryset):
		workbook = Workbook()
		sessions_sheet = workbook.active
		sessions_sheet.title = 'Sessions'
		participants_sheet = workbook.create_sheet(title='Participants')

		sessions_sheet.append([
			'Session ID',
			'Supplier',
			'Store Number',
			'Value',
			'Start Time',
			'End Time',
			'Duration (minutes)',
			'People Working',
			'Total People-Minutes',
		])
		participants_sheet.append([
			'Session ID',
			'Supplier',
			'Store Number',
			'Participant Name',
			'Joined At',
			'Left At',
		])

		sessions = queryset.select_related('supplier').prefetch_related('participants')
		for session in sessions:
			participant_rows = SessionParticipant.objects.filter(session=session).order_by('joined_at', 'id')
			total_people_minutes = 0
			for participant in participant_rows:
				participant_end = participant.left_at or session.end_time
				if participant_end is None:
					continue

				duration_seconds = (participant_end - participant.joined_at).total_seconds()
				total_people_minutes += max(duration_seconds / 60, 0)

			store_number = self.store_number(session)
			sessions_sheet.append([
				session.id,
				str(session.supplier),
				store_number,
				str(session.value),
				self._format_datetime(session.start_time),
				self._format_datetime(session.end_time),
				session.duration_minutes,
				session.people_working,
				round(total_people_minutes, 2),
			])

			for participant in participant_rows:
				participants_sheet.append([
					session.id,
					str(session.supplier),
					store_number,
					participant.name,
					self._format_datetime(participant.joined_at),
					self._format_datetime(participant.left_at),
				])

		output = BytesIO()
		workbook.save(output)
		output.seek(0)

		response = HttpResponse(
			output.getvalue(),
			content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		)
		response['Content-Disposition'] = 'attachment; filename="ssa_sessions_export.xlsx"'
		return response

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

	def _format_datetime(self, value):
		if value is None:
			return ''
		if timezone.is_naive(value):
			value = timezone.make_aware(value, timezone=utc)
		return value.astimezone(brisbane).replace(tzinfo=None)
