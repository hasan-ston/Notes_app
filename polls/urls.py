from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('details/<int:id>/', views.note_detail, name='details'),
    path('generate/<int:id>/', views.generate_questions_view, name='generate_questions'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)