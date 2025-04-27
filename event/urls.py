
from django.contrib import admin
from django.urls import path, include
import event.views as event_view
from django.conf import settings
from django.conf.urls.static import static  

urlpatterns = [
    path('dashboard/', event_view.EventDashboardView.as_view(), name='event_dashboard'),
    path('add/', event_view.AddNewEventView.as_view(), name='add_event'),

    path('<int:id>/', event_view.EventDetailsView.as_view(), name='event_detail'),
    path('edit/<int:pk>', event_view.EditEventView.as_view(), name='edit_event'),
    path('delete/<int:pk>', event_view.DeleteEventView.as_view(), name='delete_event'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
