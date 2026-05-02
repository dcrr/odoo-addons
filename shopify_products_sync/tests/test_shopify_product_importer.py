from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.component.tests.common import TransactionComponentCase


@tagged("shopify_products_sync")
class TestShopifyProductImporter(TransactionComponentCase):
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

    def _shopify_product_data(self):
        return {
            "product": {
                "id": 100,
                "title": "T-Shirt",
                "body_html": "<p>Cotton shirt</p>",
                "options": [
                    {
                        "id": 10,
                        "name": "Color",
                        "position": 1,
                        "values": ["Red", "Blue"],
                    },
                    {
                        "id": 11,
                        "name": "Size",
                        "position": 2,
                        "values": ["S", "M"],
                    },
                ],
                "variants": [
                    {
                        "id": 1001,
                        "option1": "Red",
                        "option2": "S",
                        "sku": "TS-RED-S",
                        "barcode": "100000000001",
                        "price": "10.00",
                    },
                    {
                        "id": 1002,
                        "option1": "Red",
                        "option2": "M",
                        "sku": "TS-RED-M",
                        "barcode": "100000000002",
                        "price": "11.00",
                    },
                    {
                        "id": 1003,
                        "option1": "Blue",
                        "option2": "S",
                        "sku": "TS-BLUE-S",
                        "barcode": "100000000003",
                        "price": "12.00",
                    },
                    {
                        "id": 1004,
                        "option1": "Blue",
                        "option2": "M",
                        "sku": "TS-BLUE-M",
                        "barcode": "100000000004",
                        "price": "13.00",
                    },
                ],
            }
        }

    @patch(
        "odoo.addons.shopify_products_sync.components.shopify_adapter."
        "ShopifyAdapter._request"
    )
    def test_import_product_creates_all_shopify_variants(self, mock_request):
        mock_request.return_value = self._shopify_product_data()

        template_binding = self.backend.import_shopify_product(100)
        variant_bindings = template_binding.shopify_variant_ids

        self.assertEqual(template_binding.external_id, "100")
        self.assertEqual(len(variant_bindings), 4)
        self.assertEqual(
            set(variant_bindings.mapped("external_id")),
            {"1001", "1002", "1003", "1004"},
        )
        self.assertEqual(
            variant_bindings.mapped("shopify_template_id"),
            template_binding,
        )

        template = template_binding.odoo_id
        self.assertEqual(template.name, "T-Shirt")
        self.assertEqual(len(template.product_variant_ids), 4)
        self.assertEqual(
            set(template.attribute_line_ids.mapped("attribute_id.name")),
            {"Color", "Size"},
        )
        self.assertEqual(
            set(template.product_variant_ids.mapped("default_code")),
            {"TS-RED-S", "TS-RED-M", "TS-BLUE-S", "TS-BLUE-M"},
        )

    @patch(
        "odoo.addons.shopify_products_sync.components.shopify_adapter."
        "ShopifyAdapter._request"
    )
    def test_import_product_updates_existing_variant_bindings(self, mock_request):
        data = self._shopify_product_data()
        mock_request.return_value = data

        self.backend.import_shopify_product(100)
        data["product"]["variants"][0]["sku"] = "TS-RED-S-UPDATED"
        self.backend.import_shopify_product(100)

        bindings = self.env["shopify.product.product"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("shopify_template_id.external_id", "=", "100"),
            ]
        )
        self.assertEqual(len(bindings), 4)
        self.assertIn("TS-RED-S-UPDATED", bindings.odoo_id.mapped("default_code"))
