from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from event.models import Event
from django.core.paginator import Paginator

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
import datetime
from django.http import HttpResponseForbidden
import bleach

class EventDashboardView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'event-dashboard.html'
    paginate_by = 6

    def get(self, request):
        status_filter = request.GET.get('status', '').lower()
        search_query = request.GET.get('search', '')
        events = Event.objects.all()
        if status_filter in ['upcoming', 'ongoing', 'completed', 'cancelled']:
            events = events.filter(status=status_filter)
        if search_query:
            events = events.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Calculate stats
        stats = Event.objects.aggregate(
            upcoming=Count('id', filter=Q(status='upcoming')),
            ongoing=Count('id', filter=Q(status='ongoing')),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled'))
        )

        # Paginate events
        paginator = Paginator(events.order_by('date'), self.paginate_by)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'events': page_obj,
            'stats': stats,
            'status_filter': status_filter,
            'search_query': search_query,
        }

        return render(request, self.template_name, context)

class AddNewEventView(LoginRequiredMixin, View):
    login_url = 'login'
    template_name = 'add-new-event.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        date_str = request.POST.get('date')
        location = request.POST.get('location')
        status = request.POST.get('status')
        image = request.FILES.get('image')
        if not all([title, description, date_str, location, status]):
            messages.error(request, "All required fields must be filled.")
            return render(request, self.template_name)
        valid_statuses = [choice[0] for choice in Event.STATUS_CHOICES]
        if status not in valid_statuses:
            messages.error(request, "Invalid status selected.")
            return render(request, self.template_name)
        try:
            event_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            event_date = timezone.make_aware(event_date)  # Make timezone-aware
            if event_date < timezone.now():
                messages.error(request, "Event date cannot be in the past.")
                return render(request, self.template_name)
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD HH:MM.")
            return render(request, self.template_name)

        # Create event
        try:
            event = Event(
                title=title,
                description=description,
                date=event_date,
                location=location,
                organizer=request.user,
                status=status,
                image=image
            )
            event.full_clean()  # Run model validation
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_dashboard')
        except ValidationError as e:
            messages.error(request, f"Error creating event: {e}")
            return render(request, self.template_name)
        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")
            return render(request, self.template_name)
        

class EditEventView(LoginRequiredMixin, View):
    login_url = 'login'

    template_name = 'edit-event.html'

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        # Check if user is the organizer
        if event.organizer != request.user:
            return HttpResponseForbidden("You are not authorized to edit this event.")
        return render(request, self.template_name, {'event': event})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        # Check if user is the organizer
        if event.organizer != request.user:
            return HttpResponseForbidden("You are not authorized to edit this event.")

        # Extract form data
        title = request.POST.get('title')
        description = bleach.clean(
            request.POST.get('description'),
            tags=['p', 'b', 'i', 'u', 'a', 'ul', 'ol', 'li', 'strong', 'em', 'br'],
            attributes={'a': ['href', 'target']},
            strip=True
        )
        date_str = request.POST.get('date')
        location = request.POST.get('location')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        # Validate required fields
        if not all([title, description, date_str, location, status]):
            messages.error(request, "All required fields must be filled.")
            return render(request, self.template_name, {'event': event})

        # Validate description length
        if len(description) > 10000:
            messages.error(request, "Description is too long.")
            return render(request, self.template_name, {'event': event})

        # Validate status
        valid_statuses = [choice[0] for choice in Event.STATUS_CHOICES]
        if status not in valid_statuses:
            messages.error(request, "Invalid status selected.")
            return render(request, self.template_name, {'event': event})

        # Validate and parse date
        try:
            event_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            event_date = timezone.make_aware(event_date)  # Make timezone-aware
            if event_date < timezone.now():
                messages.error(request, "Event date cannot be in the past.")
                return render(request, self.template_name, {'event': event})
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD HH:MM.")
            return render(request, self.template_name, {'event': event})

        # Update event
        try:
            event.title = title
            event.description = description  # Sanitized TinyMCE HTML
            event.date = event_date
            event.location = location
            event.status = status
            if image:
                event.image = image  # Update image only if a new one is uploaded
            event.full_clean()  # Run model validation
            event.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_dashboard')
        except ValidationError as e:
            messages.error(request, f"Error updating event: {e}")
            return render(request, self.template_name, {'event': event})
        except Exception as e:
            messages.error(request, f"Unexpected error: {e}")
            return render(request, self.template_name, {'event': event})



class DeleteEventView(LoginRequiredMixin, View):
    template_name = 'delete-event.html'
    login_url = 'login'

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user:
            return HttpResponseForbidden("You are not authorized to delete this event.")
        return render(request, self.template_name, {'event': event})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user:
            return HttpResponseForbidden("You are not authorized to delete this event.")
        
        try:
            event_title = event.title
            event.delete()
            messages.success(request, f"Event '{event_title}' deleted successfully!")
            return redirect('event_dashboard')
        except Exception as e:
            messages.error(request, f"Error deleting event: {e}")
            return render(request, self.template_name, {'event': event})
        


class EventDetailsView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, id):
        event = get_object_or_404(Event, id=id)
        context = {
            'event': event,
        }
        return render(request, 'event_detail.html', context)
    


''''
TODO:
- Event notifications setup (IN app notification along with email notification)

- Event Reminder and registering the participants in event.


'''

class EventNotificationsClass(LoginRequiredMixin, View):
    login_url = "login"
    def get(self,request):
        pass
    def post(self, request):
        pass
    