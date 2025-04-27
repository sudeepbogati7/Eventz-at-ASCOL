from django.db import models

from django.db import models
from django.conf import settings

class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=200, help_text="Title of the event")
    description = models.TextField(help_text="Detailed description of the event")
    date = models.DateTimeField(help_text="Date and time when the event will occur")
    location = models.CharField(max_length=200, help_text="Venue or location of the event")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="User who organizes the event"
    )
    image = models.ImageField(
        upload_to='events/images/',
        blank=True,
        null=True,
        help_text="Optional event poster or image"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
        help_text="Current status of the event"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the event was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the event was last updated")

    class Meta:
        ordering = ['date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title