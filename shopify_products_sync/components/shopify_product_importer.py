from odoo.fields import Command

from odoo.addons.component.core import Component


class ShopifyProductTemplateImporter(Component):
    _name = "shopify.product.template.importer"
    _inherit = "shopify.importer"
    _collection = "shopify.backend"
    _apply_on = ["shopify.product.template"]

    def run(self, external_id):
        """Import a Shopify product as an Odoo product template."""
        adapter = self.component(usage="backend.adapter")
        binder = self.binder_for()
        mapper = self.component(usage="import.mapper")

        data = adapter.read(external_id).get("product", {})
        shopify_product_id = str(data.get("id") or external_id)
        binding = binder.to_internal(shopify_product_id)
        values = {
            **mapper.map_record(data).values(),
            "backend_id": self.backend_record.id,
        }

        if binding:
            binding.write(values)
        else:
            binding = self.model.create(values)
        binder.bind(shopify_product_id, binding)

        option_values = self._sync_attribute_lines(binding, data)
        binding.odoo_id._create_variant_ids()
        imported_products = self._import_variants(binding, data, option_values)
        if imported_products:
            self._archive_missing_variants(binding, imported_products)
        return binding

    def _sync_attribute_lines(self, template_binding, data):
        option_values = self._get_shopify_option_values(data)
        product_template = template_binding.odoo_id
        product_template.attribute_line_ids.filtered(
            lambda line: line.attribute_id.name not in option_values
        ).unlink()

        for option_name, values in option_values.items():
            attribute = self._get_or_create_attribute(option_name)
            attribute_values = self.env["product.attribute.value"]
            for value in values:
                attribute_values |= self._get_or_create_attribute_value(
                    attribute, value
                )
            line = product_template.attribute_line_ids.filtered(
                lambda current_line, attribute=attribute: (
                    current_line.attribute_id == attribute
                )
            )
            line_values = {"value_ids": [Command.set(attribute_values.ids)]}
            if line:
                line.write(line_values)
            else:
                self.env["product.template.attribute.line"].create(
                    {
                        "product_tmpl_id": product_template.id,
                        "attribute_id": attribute.id,
                        **line_values,
                    }
                )
        return option_values

    def _get_shopify_option_values(self, data):
        variants = data.get("variants", [])
        option_values = {}
        for option in sorted(
            data.get("options", []), key=lambda option: option.get("position", 0)
        ):
            position = option.get("position")
            name = option.get("name")
            values = [
                value
                for value in option.get("values", [])
                if value and value != "Default Title"
            ]
            for variant in variants:
                value = variant.get(f"option{position}")
                if value and value != "Default Title" and value not in values:
                    values.append(value)
            if name and values:
                option_values[name] = values
        return option_values

    def _get_or_create_attribute(self, name):
        attribute = self.env["product.attribute"].search([("name", "=", name)], limit=1)
        if attribute:
            return attribute
        return self.env["product.attribute"].create({"name": name})

    def _get_or_create_attribute_value(self, attribute, name):
        value = self.env["product.attribute.value"].search(
            [
                ("attribute_id", "=", attribute.id),
                ("name", "=", name),
            ],
            limit=1,
        )
        if value:
            return value
        return self.env["product.attribute.value"].create(
            {
                "attribute_id": attribute.id,
                "name": name,
            }
        )

    def _import_variants(self, template_binding, data, option_values):
        imported_products = self.env["product.product"]
        importer = self.component(
            usage="importer",
            model_name="shopify.product.product",
        )
        for variant in data.get("variants", []):
            variant_binding = importer.run(
                template_binding,
                variant,
                option_values,
            )
            imported_products |= variant_binding.odoo_id
        return imported_products

    def _archive_missing_variants(self, template_binding, imported_products):
        product_template = template_binding.odoo_id
        extra_products = product_template.product_variant_ids - imported_products
        if extra_products:
            extra_products.active = False


class ShopifyProductImporter(Component):
    _name = "shopify.product.importer"
    _inherit = "shopify.importer"
    _collection = "shopify.backend"
    _apply_on = ["shopify.product.product"]

    def run(self, template_binding, variant, option_values):
        """Import one Shopify variant as an Odoo product variant."""
        binder = self.binder_for()
        mapper = self.component(usage="import.mapper")
        external_id = str(variant["id"])

        product = self._get_or_create_variant(
            template_binding.odoo_id,
            variant,
            option_values,
        )
        product.write(mapper.map_record(variant).values())

        binding = binder.to_internal(external_id)
        values = {
            "odoo_id": product.id,
            "backend_id": self.backend_record.id,
            "shopify_template_id": template_binding.id,
        }
        if binding:
            binding.write(values)
        else:
            binding = self.model.create(values)
        binder.bind(external_id, binding)
        return binding

    def _get_or_create_variant(self, product_template, variant, option_values):
        combination = self._get_variant_combination(
            product_template, variant, option_values
        )
        variants = product_template.with_context(active_test=False).product_variant_ids
        product = variants.filtered(
            lambda product, combination=combination: (
                set(product.product_template_attribute_value_ids.ids)
                == set(combination.ids)
            )
        )[:1]
        if product:
            if not product.active:
                product.active = True
            return product
        return self.env["product.product"].create(
            {
                "product_tmpl_id": product_template.id,
                "product_template_attribute_value_ids": [Command.set(combination.ids)],
            }
        )

    def _get_variant_combination(self, product_template, variant, option_values):
        combination = self.env["product.template.attribute.value"]
        for position, option_name in enumerate(option_values, start=1):
            value_name = variant.get(f"option{position}")
            if not value_name:
                continue
            line = product_template.attribute_line_ids.filtered(
                lambda current_line, option_name=option_name: (
                    current_line.attribute_id.name == option_name
                )
            )
            combination |= line.product_template_value_ids.filtered(
                lambda template_value, value_name=value_name: (
                    template_value.name == value_name
                )
            )[:1]
        return combination
