from http.client import HTTPException
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import ItemCreateForm, ExchangeProposalForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login


@login_required
def main_page(request):
    if request.method == 'GET':
        return render(request, 'ads/main.html')
    else:
        return HTTPException("Method not allowed")


def my_items_page(request):
    if request.method == 'GET':
        return render(request, 'ads/my_items.html')
    else:
        return HTTPException("Method not allowed")


def my_request_page(request):
    if request.method == 'GET':
        return render(request, 'ads/my_requests.html')
    else:
        return HTTPException("Method not allowed")


def my_received_requests_page(request):
    if request.method == 'GET':
        return render(request, 'ads/my_received_requests.html')
    else:
        return HTTPException("Method not allowed")


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('Main page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'ads/register.html', {'form': form})



