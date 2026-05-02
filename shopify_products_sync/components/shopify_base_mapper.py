from odoo.addons.component.core import AbstractComponent


class ShopifyImportMapper(AbstractComponent):
    """Base mapper for Shopify imports.

    This component provides a foundation for mapping data from Shopify
    API responses to Odoo models.
    """

    _name = "shopify.import.mapper"
    _inherit = "base.import.mapper"
    _collection = "shopify.backend"
