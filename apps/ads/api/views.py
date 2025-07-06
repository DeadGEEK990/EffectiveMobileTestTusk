from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from ..models import ItemsModel, CategoryModel, ExchangeProposalModel
from .serializers import (
    ItemPreviewSerializer,
    CategorySerializer,
    ExchangeProposalSerializer,
    ItemCreateSerializer,
)
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ItemsPreviewViewset(viewsets.ModelViewSet):
    serializer_class = ItemPreviewSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        "category": ["exact", "in"],
        "condition": ["exact"],
    }
    search_fields = ["title", "description"]

    def get_queryset(self):
        return ItemsModel.objects.exclude(user=self.request.user)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class MyItemsViewset(viewsets.ModelViewSet):
    serializer_class = ItemPreviewSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        "category": ["exact", "in"],
        "condition": ["exact"],
    }
    search_fields = ["title", "description"]

    def get_queryset(self):
        return ItemsModel.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ItemCreateSerializer
        return ItemPreviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied("Вы не можете редактировать этот товар")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied("Вы не можете удалить этот товар")
        return super().destroy(request, *args, **kwargs)


class MyExchangeProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_queryset(self):
        user = self.request.user
        return ExchangeProposalModel.objects.filter(ad_sender__user=user)

    def get_object(self):
        proposal = get_object_or_404(
            ExchangeProposalModel,
            pk=self.kwargs["pk"],
        )
        if (
            proposal.ad_sender.user != self.request.user
            and proposal.ad_receiver.user != self.request.user
        ):
            raise PermissionDenied("У вас нет доступа к этому предложению.")
        return proposal

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.ad_sender.user != request.user:
            return Response({"detail": "Вы не можете удалить этот запрос"}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        queryset = ExchangeProposalModel.objects.filter(
            ad_sender__user=request.user
        ).order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def received(self, request):
        queryset = ExchangeProposalModel.objects.filter(
            ad_receiver__user=request.user
        ).order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        proposal = self.get_object()

        if proposal.ad_receiver.user != request.user:
            return Response({"detail": "Вы не можете принять этот запрос"}, status=403)

        if proposal.status != "pending":
            return Response({"detail": "Запрос уже обработан"}, status=400)

        with transaction.atomic():
            sender_item = proposal.ad_sender
            receiver_item = proposal.ad_receiver

            sender_user = sender_item.user
            receiver_user = receiver_item.user

            sender_item.user = receiver_user
            receiver_item.user = sender_user

            sender_item.save()
            receiver_item.save()

            proposal.status = "accepted"
            proposal.save()

            ExchangeProposalModel.objects.filter(status="pending").filter(
                Q(ad_sender=sender_item)
                | Q(ad_receiver=sender_item)
                | Q(ad_sender=receiver_item)
                | Q(ad_receiver=receiver_item)
            ).exclude(id=proposal.id).update(status="declined")

        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"], url_path="decline")
    def decline(self, request, pk=None):
        proposal = self.get_object()

        if proposal.ad_receiver.user != request.user:
            return Response(
                {"detail": "Вы не можете отклонить этот запрос"}, status=403
            )

        if proposal.status != "pending":
            return Response({"detail": "Запрос уже обработан"}, status=400)

        proposal.status = "declined"
        proposal.save()

        return Response({"status": "declined"})

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        proposal = self.get_object()
        if proposal.ad_sender.user != request.user:
            return Response({"detail": "Вы не можете отменить этот запрос"}, status=403)
        if proposal.status != "pending":
            return Response({"detail": "Запрос уже обработан"}, status=400)
        proposal.status = "declined"
        proposal.save()
        return Response({"status": "cancelled"})


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def get_categories(request):
    categories = CategoryModel.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def current_user(request):
    if request.user.is_authenticated:
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            }
        )
    return Response({"error": "Not authenticated"}, status=401)
