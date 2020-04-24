from django.urls import path

from . import views

urlpatterns = [
    path('visited_links/', views.VisitedLinksView.as_view(), name='visited-links'),
    path('visited_domains/', views.VisitedDomainsView.as_view(), name='visited-domains')
]