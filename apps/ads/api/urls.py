from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemsPreviewViewset, current_user, MyItemsViewset, MyExchangeProposalViewSet, get_categories

router = DefaultRouter()
router.register(r'items', ItemsPreviewViewset, basename='items')
router.register(r'my-items', MyItemsViewset, basename='my-items')
router.register(r'exchange-proposals', MyExchangeProposalViewSet, basename='exchange-proposals')

urlpatterns = [
    path('', include(router.urls)),
    path('current-user/', current_user, name='current-user'),
    path('categories/', get_categories, name='get-categorys')
]