{
    "name": "Shopify Product Synchronizer",
    "version": "18.0.0.0.0",
    "license": "LGPL-3",
    "category": "Sales",
    "author": "Diana C. Rojas R.",
    "depends": ["sale_management", "connector"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/shopify_backend_view.xml",
        "views/shopify_product_view.xml",
        "wizard/shopify_sync_wizard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "shopify_products_sync/static/src/scss/notification.scss",
        ],
    },
    "test": [
        "tests/test_shopify_backend.py",
        "tests/test_shopify_product_importer.py",
        "tests/test_shopify_sync.py",
    ],
    "installable": True,
}
