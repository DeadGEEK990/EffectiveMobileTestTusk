from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ItemsPreviewViewset,
    current_user,
    MyItemsViewset,
    MyExchangeProposalViewSet,
    get_categories,
)
from drf_spectacular.views import SpectacularAPIView
from django.views.generic import TemplateView


router = DefaultRouter()
router.register(r"items", ItemsPreviewViewset, basename="items")
router.register(r"my-items", MyItemsViewset, basename="my-items")
router.register(
    r"exchange-proposals", MyExchangeProposalViewSet, basename="exchange-proposals"
)


urlpatterns = [
    path("", include(router.urls)),
    path("current-user/", current_user, name="current-user"),
    path("categories/", get_categories, name="get-categorys"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        TemplateView.as_view(
            template_name="swagger-ui.html", extra_context={"schema_url": "schema"}
        ),
        name="swagger-ui",
    ),
]
