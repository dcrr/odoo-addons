from odoo.addons.component.core import AbstractComponent


class ShopifyImporter(AbstractComponent):
    """Base importer for Shopify resources."""

    _name = "shopify.importer"
    _inherit = "base.importer"
    _collection = "shopify.backend"
