from urllib.parse import urlsplit

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import identity_exact


class ShopifyBackend(models.Model):
    _name = "shopify.backend"
    _inherit = "connector.backend"
    _description = "Shopify Backend"

    _SHOPIFY_IMPORT_CHANNEL = "root.shopify_import_product"

    @api.model
    def _select_versions(self):
        return [("2025-10", "2025-10")]

    @api.model
    def _normalize_shop_name(self, shop_name):
        if not shop_name:
            return False

        shop_name = shop_name.strip().lower()
        if "://" not in shop_name:
            shop_name = f"https://{shop_name}"

        hostname = urlsplit(shop_name).hostname or ""
        return hostname.removesuffix(".myshopify.com")

    @api.onchange("shop_name")
    def _onchange_shop_name(self):
        for rec in self:
            normalized_shop_name = rec._normalize_shop_name(rec.shop_name)
            if normalized_shop_name:
                rec.shop_name = normalized_shop_name

    @api.depends("shop_name")
    def _compute_host(self):
        for rec in self:
            shop_name = rec._normalize_shop_name(rec.shop_name)
            rec.host = shop_name and f"https://{shop_name}.myshopify.com"

    name = fields.Char()
    shop_name = fields.Char(
        required=True,
        help="Shop name without domain. e.g. 'myshop'.",
    )
    host = fields.Char(
        compute="_compute_host",
        help="Computed from shop name.",
    )
    api_key = fields.Char(string="API Key", required=True)
    api_token = fields.Char(string="API Token", required=True)
    api_version = fields.Selection(
        selection="_select_versions",
        string="API Version",
        required=True,
        default="2025-10",
    )
    active = fields.Boolean(default=True)

    def _get_shopify_shop_info(self):
        self.ensure_one()
        with self.work_on("shopify.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            response = adapter._request("GET", "shop.json")
        return response.get("shop", {})

    def test_connection(self):
        self.ensure_one()

        try:
            shop = self._get_shopify_shop_info()
        except Exception as e:
            raise UserError(
                _("Error connecting to Shopify:\n%(error)s", error=str(e))
            ) from e

        message = _(
            "Connected to Shopify successfully.\n\n"
            "Shop: %(shop_name)s\n"
            "Domain: %(domain)s",
            shop_name=shop.get("name") or self.name or self.shop_name,
            domain=shop.get("domain") or self.host,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "className": "o_shopify_connection_notification",
                "title": _("Shopify connection test"),
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }

    def import_shopify_product(self, external_id):
        with self.work_on("shopify.product.template") as work:
            importer = work.component(usage="importer")
            return importer.run(external_id)

    def import_products(self):
        self.ensure_one()

        with self.work_on("shopify.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            products = adapter.search()

        if not products:
            raise UserError(_("No products found in Shopify"))

        for external_product in products:
            external_id = external_product.get("id")
            external_name = external_product.get("title")
            job_description = _(
                "Import product '%(external_name)s' (%(external_id)s) "
                "from Shopify backend '%(backend_name)s'",
                external_name=external_name,
                external_id=external_id,
                backend_name=self.name,
            )
            self.with_delay(
                priority=2,
                identity_key=identity_exact,
                channel=self._SHOPIFY_IMPORT_CHANNEL,
                max_retries=3,
                description=job_description,
            ).import_shopify_product(external_id)
        return True
