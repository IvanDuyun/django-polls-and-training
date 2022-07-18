from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('author_balance/', views.author_balance_list, name='author_balance_list'),
    path('author_balance/<int:pk>/', views.author_balance_detail, name='author_balance_detail'),
]
