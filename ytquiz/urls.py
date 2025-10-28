from django.urls import path
from .views import index,QuizAPIView
urlpatterns = [
    path('', index),
    path('quiz_view/', QuizAPIView.as_view()),
]