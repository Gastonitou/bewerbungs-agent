"""Stripe integration service (webhook handlers only, no secrets in code)."""

from typing import Optional, Dict, Any
from datetime import datetime

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

from sqlalchemy.orm import Session

from bewerbungs_agent.models import User, SubscriptionPlan
from bewerbungs_agent.services.user_service import UserService
from bewerbungs_agent.utils.config import get_settings


class StripeService:
    """
    Service for handling Stripe subscriptions.
    NOTE: This is a stub implementation for SaaS readiness.
    Real implementation requires proper webhook verification and error handling.
    """

    def __init__(self):
        """Initialize Stripe service."""
        if not STRIPE_AVAILABLE:
            raise ImportError(
                "Stripe not available. Install with: pip install stripe"
            )
        
        settings = get_settings()
        if settings.stripe_secret_key:
            stripe.api_key = settings.stripe_secret_key

    @staticmethod
    def create_customer(email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Stripe customer.
        Call this when a new user signs up.
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                'source': 'bewerbungs-agent',
            }
        )
        return customer

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for subscription.
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session

    @staticmethod
    def handle_webhook(
        payload: bytes,
        signature: str,
        webhook_secret: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Handle Stripe webhook events.
        This should be called from your web server endpoint.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except ValueError:
            # Invalid payload
            return None
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return None

        return event

    @staticmethod
    def process_subscription_created(
        db: Session,
        event_data: Dict[str, Any],
    ) -> bool:
        """
        Process subscription.created webhook.
        Update user plan when subscription is created.
        """
        subscription = event_data.get('object', {})
        customer_id = subscription.get('customer')
        
        # Get user by Stripe customer ID
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        
        if not user:
            return False
        
        # Determine plan from subscription metadata or price
        # In production, map price IDs to plans
        plan_map = {
            'price_pro_monthly': SubscriptionPlan.PRO,
            'price_agency_monthly': SubscriptionPlan.AGENCY,
        }
        
        price_id = subscription.get('items', {}).get('data', [{}])[0].get('price', {}).get('id')
        new_plan = plan_map.get(price_id, SubscriptionPlan.FREE)
        
        UserService.update_user_plan(db, user.id, new_plan)
        return True

    @staticmethod
    def process_subscription_deleted(
        db: Session,
        event_data: Dict[str, Any],
    ) -> bool:
        """
        Process subscription.deleted webhook.
        Downgrade user to free plan when subscription is cancelled.
        """
        subscription = event_data.get('object', {})
        customer_id = subscription.get('customer')
        
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()
        
        if not user:
            return False
        
        # Downgrade to free
        UserService.update_user_plan(db, user.id, SubscriptionPlan.FREE)
        return True

    @staticmethod
    def process_invoice_paid(
        db: Session,
        event_data: Dict[str, Any],
    ) -> bool:
        """
        Process invoice.paid webhook.
        Could be used for usage tracking or accounting.
        """
        # Implement invoice tracking if needed
        return True

    @staticmethod
    def get_subscription(customer_id: str) -> Optional[Dict[str, Any]]:
        """Get active subscription for a customer."""
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='active',
            limit=1,
        )
        
        if subscriptions.data:
            return subscriptions.data[0]
        
        return None

    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription."""
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        subscription = stripe.Subscription.delete(subscription_id)
        return subscription
