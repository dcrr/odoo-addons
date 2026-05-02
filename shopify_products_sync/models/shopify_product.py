from odoo import fields, models


class ShopifyProductTemplate(models.Model):
    _name = "shopify.product.template"
    _inherit = "external.binding"
    _inherits = {"product.template": "odoo_id"}
    _description = "Shopify product template binding"
    _rec_name = "odoo_id"

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
    )
    backend_id = fields.Many2one(
        comodel_name="shopify.backend",
        required=True,
        ondelete="restrict",
    )
    external_id = fields.Char(string="Shopify Product ID", index=True)
    shopify_variant_ids = fields.One2many(
        comodel_name="shopify.product.product",
        inverse_name="shopify_template_id",
        string="Shopify Variants",
    )

    _sql_constraints = [
        (
            "shopify_product_template_backend_external_uniq",
            "unique(backend_id, external_id)",
            "A Shopify product with this external ID already exists for this backend.",
        ),
    ]


class ShopifyProduct(models.Model):
    _name = "shopify.product.product"
    _inherit = "external.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "Shopify product variant binding"
    _rec_name = "odoo_id"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
    )
    backend_id = fields.Many2one(
        comodel_name="shopify.backend",
        required=True,
        ondelete="restrict",
    )
    external_id = fields.Char(string="Shopify Variant ID", index=True)
    shopify_template_id = fields.Many2one(
        comodel_name="shopify.product.template",
        string="Shopify Product",
        required=True,
        ondelete="cascade",
        index=True,
    )

    _sql_constraints = [
        (
            "shopify_product_product_backend_external_uniq",
            "unique(backend_id, external_id)",
            "A Shopify variant with this external ID already exists for this backend.",
        ),
    ]
