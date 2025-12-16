from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('details/<int:id>/', views.note_detail, name='details'),
    path('generate/<int:id>/', views.generate_questions_view, name='generate_questions'),
    path('questions/<int:question_id>/toggle/', views.toggle_review, name='toggle_review'),
    path('api/generate-questions/', views.api_generate_questions, name='api_generate_questions'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
