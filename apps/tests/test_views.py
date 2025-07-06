import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.ads.models import ItemsModel, CategoryModel, ExchangeProposalModel


# Фикстуры


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="user1", password="pass")


@pytest.fixture
def user2():
    return User.objects.create_user(username="user2", password="pass")


@pytest.fixture
def category():
    return CategoryModel.objects.create(title="Телефоны")


@pytest.fixture
def item1(user, category):
    return ItemsModel.objects.create(
        user=user,
        title="iPhone 13",
        description="Состояние идеальное",
        image_url="http://example.com/image.jpg",
        category=category,
        condition="new",
    )


@pytest.fixture
def item2(user2, category):
    return ItemsModel.objects.create(
        user=user2,
        title="Samsung S21",
        description="Почти новый",
        image_url="http://example.com/image2.jpg",
        category=category,
        condition="old",
    )


# Тесты


@pytest.mark.django_db
def test_create_item(client, user, category):
    client.login(username="user1", password="pass")
    response = client.post(
        "/api/v1/my-items/",
        {
            "title": "iPhone 14",
            "description": "Как новый",
            "image_url": "http://example.com/image3.jpg",
            "category": category.id,
            "condition": "new",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["title"] == "iPhone 14"


@pytest.mark.django_db
def test_edit_item(client, user, item1):
    client.login(username="user1", password="pass")
    url = f"/api/v1/my-items/{item1.id}/"
    response = client.patch(url, {"title": "iPhone 13 Pro"}, format="json")
    assert response.status_code == 200
    assert response.data["title"] == "iPhone 13 Pro"


@pytest.mark.django_db
def test_delete_item(client, user, item1):
    client.login(username="user1", password="pass")
    url = f"/api/v1/my-items/{item1.id}/"
    response = client.delete(url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_search_items(client, user2, item1):
    client.login(username="user2", password="pass")
    response = client.get("/api/v1/items/?search=iPhone")
    assert response.status_code == 200
    assert len(response.data["results"]) > 0


@pytest.mark.django_db
def test_send_exchange_proposal(client, user2, item1, item2):
    client.login(username="user2", password="pass")
    response = client.post(
        "/api/v1/exchange-proposals/",
        {
            "ad_sender_id": item2.id,
            "ad_receiver_id": item1.id,
            "comment": "Обменяешься?",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.data["comment"] == "Обменяешься?"


@pytest.mark.django_db
def test_accept_proposal(client, user2, user, item1, item2):
    proposal = ExchangeProposalModel.objects.create(
        ad_sender=item2, ad_receiver=item1, comment="Давай меняться"
    )
    client.login(username="user1", password="pass")
    url = f"/api/v1/exchange-proposals/{proposal.id}/accept/"
    response = client.post(url)
    assert response.status_code == 200
    assert response.data["status"] == "accepted"


@pytest.mark.django_db
def test_decline_proposal(client, user2, user, item1, item2):
    proposal = ExchangeProposalModel.objects.create(
        ad_sender=item2, ad_receiver=item1, comment="Давай меняться"
    )
    client.login(username="user1", password="pass")
    url = f"/api/v1/exchange-proposals/{proposal.id}/decline/"
    response = client.post(url)
    assert response.status_code == 200
    assert response.data["status"] == "declined"
