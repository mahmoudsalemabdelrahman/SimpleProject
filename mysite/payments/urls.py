from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/', lambda request: render(request, 'payments/success.html'), name='payment_success'),
    path('cancel/', lambda request: render(request, 'payments/cancel.html'), name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
