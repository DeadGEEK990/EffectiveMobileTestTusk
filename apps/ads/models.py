from django.db import models
from django.contrib.auth.models import User


class CategoryModel(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class ItemsModel(models.Model):
    CONDITION_CHOICES = [("old", "б/у"), ("new", "новый")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=50,
    )
    description = models.CharField(max_length=500)
    image_url = (
        models.URLField()
    )  # Не очень хорошая идея хранить URL, лучше использовать ImageField, но в ТЗ именно url
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    condition = models.CharField(max_length=5, choices=CONDITION_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ExchangeProposalModel(models.Model):
    # Варианты состояния запроса
    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("accepted", "Принято"),
        ("declined", "Отклонено"),
    ]

    ad_sender = models.ForeignKey(
        ItemsModel, related_name="sent_proposals", on_delete=models.CASCADE
    )
    ad_receiver = models.ForeignKey(
        ItemsModel, related_name="received_proposals", on_delete=models.CASCADE
    )
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
