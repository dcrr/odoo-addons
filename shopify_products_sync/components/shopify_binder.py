from odoo.addons.component.core import Component


class ShopifyProductBinder(Component):
    _name = "shopify.product.binder"
    _inherit = "base.binder"
    _collection = "shopify.backend"
    _apply_on = "shopify.product.product"


class ShopifyProductTemplateBinder(Component):
    _name = "shopify.product.template.binder"
    _inherit = "base.binder"
    _collection = "shopify.backend"
    _apply_on = "shopify.product.template"
