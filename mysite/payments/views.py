import stripe
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import Payment
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    if request.method == "POST":
        # Create a Stripe Checkout Session
        domain_url = settings.SITE_URL
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": settings.STRIPE_CURRENCY,
                        "product_data": {
                            "name": "Premium Subscription",
                        },
                        "unit_amount": 5000,  # amount in cents (e.g., $50.00)
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=domain_url + "/payments/success/",
                cancel_url=domain_url + "/payments/cancel/",
            )
            # Save a pending payment record
            Payment.objects.create(
                user=request.user,
                stripe_payment_intent_id=checkout_session.payment_intent,
                amount=checkout_session.amount_total / 100,
                currency=checkout_session.currency,
                status="created",
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({"error": str(e)})
    return render(request, "payments/checkout.html")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=session["payment_intent"])
            payment.status = "succeeded"
            payment.save()
        except Payment.DoesNotExist:
            pass
    return HttpResponse(status=200)
