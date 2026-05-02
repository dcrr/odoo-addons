from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopifyProductTemplateImportMapper(Component):
    _name = "shopify.product.template.import.mapper"
    _inherit = "shopify.import.mapper"
    _collection = "shopify.backend"
    _apply_on = ["shopify.product.template"]

    direct = [
        ("title", "name"),
        ("body_html", "description"),
    ]

    @mapping
    def price(self, record):
        variants = record.get("variants", [])
        if variants:
            return {"list_price": float(variants[0].get("price", 0.0))}
        return {}


class ShopifyProductImportMapper(Component):
    _name = "shopify.product.import.mapper"
    _inherit = "shopify.import.mapper"
    _collection = "shopify.backend"
    _apply_on = ["shopify.product.product"]

    @mapping
    def variant_fields(self, record):
        return {
            "default_code": record.get("sku") or False,
            "barcode": record.get("barcode") or False,
        }
