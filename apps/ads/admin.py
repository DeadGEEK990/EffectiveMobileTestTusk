from django.contrib import admin
from .models import CategoryModel, ItemsModel, ExchangeProposalModel

@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title",)
    search_fields = ("title",)
    fields = ("title",)


@admin.register(ItemsModel)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "description", "image_url", "category", "condition", "created_at")
    list_filter = ("category", "condition")
    search_fields = ("user__username", "title")
    fields = ("user", "title", "description", "image_url", "category", "condition")


@admin.register(ExchangeProposalModel)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "ad_sender", "ad_receiver", "comment", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("ad_sender", "ad_receiver")
    fields = ("ad_sender", "ad_receiver", "comment", "status")




