from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APITestCase
from .models import NewsletterSubscription, Product

class StoreTests(APITestCase):
    @classmethod
    def setUpTestData(cls): call_command("seed_store", verbosity=0)

    def test_seed_has_one_hundred_products(self): self.assertEqual(Product.objects.count(), 100)

    def test_catalog_and_search(self):
        response = self.client.get("/api/products/?q=robot")
        self.assertEqual(response.status_code, 200); self.assertGreater(response.data["count"], 0)

    def test_chat_rejects_unrelated_question(self):
        response = self.client.post("/api/chat/", {"message": "Write a poem about the moon", "session_id": "test"}, format="json")
        self.assertEqual(response.status_code, 200); self.assertIn("only help", response.data["answer"])

    def test_chat_lists_every_category(self):
        response = self.client.post("/api/chat/", {"message": "Which project categories are available?", "session_id": "categories"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("10 project categories", response.data["answer"])
        self.assertEqual(len(response.data["links"]), 10)

    def test_chat_lists_low_and_out_of_stock_products(self):
        low = self.client.post("/api/chat/", {"message": "Show me low stock items", "session_id": "low"}, format="json")
        out = self.client.post("/api/chat/", {"message": "Show me out of stock items", "session_id": "out"}, format="json")
        self.assertEqual(low.status_code, 200)
        self.assertEqual(out.status_code, 200)
        self.assertGreater(len(low.data["links"]), 0)
        self.assertGreater(len(out.data["links"]), 0)

    @patch("store.views.send_email_async")
    def test_guest_checkout_returns_before_email_delivery(self, send_email):
        product = Product.objects.filter(stock__gt=0).first()
        response = self.client.post("/api/checkout/", {
            "customer_name": "Test Buyer", "email": "buyer@example.com", "phone": "9876543210",
            "address": "1 Test Street", "city": "Chennai", "state": "Tamil Nadu", "postal_code": "600001",
            "payment_method": "cod", "items": [{"product_id": product.id, "quantity": 1}],
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["number"].startswith("PN-"))
        send_email.assert_called_once()

    @patch("store.views.send_email_async")
    def test_newsletter_subscription(self, send_email):
        response = self.client.post("/api/subscribe/", {"email": "builder@example.com"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(NewsletterSubscription.objects.filter(email="builder@example.com").exists())
        send_email.assert_called_once()

    def test_authenticated_cart(self):
        user = User.objects.create_user("buyer", password="safe-password")
        self.client.force_authenticate(user); product = Product.objects.filter(stock__gt=0).first()
        response = self.client.post("/api/cart/", {"product_id": product.id, "quantity": 1}, format="json")
        self.assertEqual(response.status_code, 201); self.assertEqual(len(response.data["items"]), 1)
