from odoo.addons.component.core import Component


class ShopifyProductTemplateAdapter(Component):
    # Connector adapter methods intentionally implement the transport API.
    # pylint: disable=method-required-super
    _name = "shopify.product.template.adapter"
    _inherit = "shopify.adapter"
    _collection = "shopify.backend"
    _apply_on = "shopify.product.template"

    def read(self, external_id):
        return self._request("GET", f"products/{external_id}.json")

    def search(self, params=None):
        data = self._request("GET", "products.json", params=params)
        return data.get("products", [])


class ShopifyProductAdapter(Component):
    # Connector adapter methods intentionally implement the transport API.
    # pylint: disable=method-required-super
    _name = "shopify.product.adapter"
    _inherit = "shopify.adapter"
    _collection = "shopify.backend"
    _apply_on = "shopify.product.product"
