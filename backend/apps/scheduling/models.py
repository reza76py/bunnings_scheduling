from django.db import models


class Supplier(models.Model):
	name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return self.name


class CountingSession(models.Model):
	supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='sessions')
	value = models.DecimalField(max_digits=10, decimal_places=2)
	people_working = models.TextField()
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	duration_minutes = models.PositiveIntegerField(default=0, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if self.start_time and self.end_time:
			duration_seconds = (self.end_time - self.start_time).total_seconds()
			self.duration_minutes = max(int(duration_seconds // 60), 0)
		super().save(*args, **kwargs)
