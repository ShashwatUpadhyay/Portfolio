from django.urls import path
from ytquiz.views import index,QuizAPIView
urlpatterns = [
    path('quiz_view/', QuizAPIView.as_view()),
]