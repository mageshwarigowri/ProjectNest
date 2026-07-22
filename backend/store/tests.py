from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APITestCase
from .models import Product

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

    def test_authenticated_cart(self):
        user = User.objects.create_user("buyer", password="safe-password")
        self.client.force_authenticate(user); product = Product.objects.filter(stock__gt=0).first()
        response = self.client.post("/api/cart/", {"product_id": product.id, "quantity": 1}, format="json")
        self.assertEqual(response.status_code, 201); self.assertEqual(len(response.data["items"]), 1)
