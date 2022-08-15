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
    path('new/', views.QuestionCreateView.as_view(), name='question_new'),
    path('<int:pk>/update/', views.QuestionUpdateView.as_view(), name='question_update'),
    path('new_m/', views.question_create_view, name='question_new_m'),  # m - manually
    path('update_m/<int:pk>', views.question_update_view, name='question_update_m'),
    path('agreement/<int:profile_id>', views.set_agreement, name='agreement'),
    path('for_test_cache_with_decorator/', views.view_for_test_cache_with_decorator),
    path('for_test_cache_manually/', views.view_for_test_cache_manually),
]
