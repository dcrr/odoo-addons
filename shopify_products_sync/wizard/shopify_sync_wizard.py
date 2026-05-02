from odoo import fields, models


class ShopifySyncWizard(models.TransientModel):
    _name = "shopify.sync.wizard"
    _description = "Shopify Synchronization Wizard"

    backend_id = fields.Many2one(
        "shopify.backend",
        string="Shopify Backend",
        required=True,
        default=lambda self: self.env["shopify.backend"].search([], limit=1),
        domain=[("active", "=", True)],
        help="The Shopify backend to synchronize from.",
    )
    import_products = fields.Boolean(
        default=True,
        help="Check to import products from Shopify.",
    )

    def action_sync(self):
        self.ensure_one()
        if self.import_products:
            self.backend_id.import_products()
        return {"type": "ir.actions.act_window_close"}
