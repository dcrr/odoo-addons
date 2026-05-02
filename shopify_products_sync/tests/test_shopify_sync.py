from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("shopify_products_sync")
class TestShopifySyncWizard(TransactionCase):
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
        self.wizard = self.env["shopify.sync.wizard"].create(
            {
                "backend_id": self.backend.id,
                "import_products": True,
            }
        )

    @patch(
        "odoo.addons.shopify_products_sync.models.shopify_backend.ShopifyBackend.import_products",
        create=True,
    )
    def test_action_sync_with_products(self, mock_import_products):
        result = self.wizard.action_sync()
        self.assertEqual(result, {"type": "ir.actions.act_window_close"})
        mock_import_products.assert_called_once()

    def test_action_sync_without_products(self):
        self.wizard.import_products = False
        result = self.wizard.action_sync()
        self.assertEqual(result, {"type": "ir.actions.act_window_close"})
