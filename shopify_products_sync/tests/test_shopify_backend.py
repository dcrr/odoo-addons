from unittest.mock import MagicMock, patch

from odoo.tests import TransactionCase, tagged


@tagged("shopify_products_sync")
class TestShopifyBackend(TransactionCase):
    def setUp(self):
        super().setUp()
        self.backend = self.env["shopify.backend"].create(
            {
                "name": "Test Backend",
                "shop_name": "testshop",
                "api_key": "test_key",
                "api_token": "test_token",
                "api_version": "2025-10",
            }
        )

    def test_normalize_shop_name(self):
        self.assertEqual(
            self.backend._normalize_shop_name("https://testshop.myshopify.com"),
            "testshop",
        )
        self.assertEqual(
            self.backend._normalize_shop_name("testshop.myshopify.com"),
            "testshop",
        )
        self.assertEqual(
            self.backend._normalize_shop_name("TestShop"),
            "testshop",
        )
        self.assertFalse(self.backend._normalize_shop_name(""))

    def test_compute_host(self):
        self.backend.shop_name = "testshop"
        self.backend._compute_host()
        self.assertEqual(self.backend.host, "https://testshop.myshopify.com")

    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.work_on",
        create=True,
    )
    def test_get_shopify_shop_info(self, mock_work_on):
        mock_adapter = MagicMock()
        mock_adapter._request.return_value = {"shop": {"name": "Test Shop"}}
        mock_work_on.return_value.__enter__.return_value.component.return_value = (
            mock_adapter
        )

        result = self.backend._get_shopify_shop_info()
        self.assertEqual(result, {"name": "Test Shop"})
        mock_adapter._request.assert_called_once_with("GET", "shop.json")

    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.work_on",
        create=True,
    )
    def test_test_connection_success(self, mock_work_on):
        mock_adapter = MagicMock()
        mock_adapter._request.return_value = {
            "shop": {"name": "Test Shop", "domain": "testshop.myshopify.com"}
        }
        mock_work_on.return_value.__enter__.return_value.component.return_value = (
            mock_adapter
        )

        result = self.backend.test_connection()
        self.assertIn("Connected to Shopify successfully", result["params"]["message"])

    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.work_on",
        create=True,
    )
    def test_test_connection_failure(self, mock_work_on):
        mock_adapter = MagicMock()
        mock_adapter._request.side_effect = Exception("Connection error")
        mock_work_on.return_value.__enter__.return_value.component.return_value = (
            mock_adapter
        )

        with self.assertRaises(Exception):
            self.backend.test_connection()

    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.work_on",
        create=True,
    )
    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.with_delay",
        create=True,
    )
    def test_import_products(self, mock_with_delay, mock_work_on):
        mock_adapter = MagicMock()
        mock_adapter.search.return_value = [
            {"id": 1, "title": "Product 1"},
            {"id": 2, "title": "Product 2"},
        ]
        mock_work_on.return_value.__enter__.return_value.component.return_value = (
            mock_adapter
        )

        result = self.backend.import_products()
        self.assertTrue(result)
        self.assertEqual(mock_with_delay.call_count, 2)
        mock_adapter.search.assert_called_once()

    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.work_on",
        create=True,
    )
    def test_import_products_no_products(self, mock_work_on):
        mock_adapter = MagicMock()
        mock_adapter.search.return_value = []
        mock_work_on.return_value.__enter__.return_value.component.return_value = (
            mock_adapter
        )

        with self.assertRaises(Exception):
            self.backend.import_products()
