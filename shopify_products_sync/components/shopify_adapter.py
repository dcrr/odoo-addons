import logging

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import SSLError, Timeout

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)

SHOPIFY_REQUEST_TIMEOUT = 30


class ShopifyAdapter(Component):
    # Connector adapter methods intentionally implement the transport API.
    # pylint: disable=method-required-super
    _name = "shopify.adapter"
    _inherit = "base.backend.adapter"
    _usage = "backend.adapter"
    _collection = "shopify.backend"

    def _get_headers(self):
        return {
            "X-Shopify-Access-Token": self.backend_record.api_token,
            "Content-Type": "application/json",
        }

    def _get_base_url(self):
        return (
            f"{self.backend_record.host.rstrip('/')}/admin/api/"
            f"{self.backend_record.api_version}"
        )

    def _request(self, method, path, params=None, data=None):
        url = f"{self._get_base_url()}/{path.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                json=data,
                timeout=SHOPIFY_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            if not response.content:
                return {}
            return response.json()

        except SSLError as e:
            _logger.error("SSL error connecting to Shopify (%s): %s", url, e)
            raise
        except Timeout:
            _logger.error("Timeout connecting to Shopify (%s)", url)
            raise
        except RequestsConnectionError as e:
            _logger.error("Connection error connecting to Shopify (%s): %s", url, e)
            raise
        except requests.HTTPError:
            _logger.error(
                "HTTP error %s calling Shopify (%s): %s",
                response.status_code,
                url,
                response.text,
            )
            raise

    def read(self, external_id):
        return self._request("GET", f"products/{external_id}.json")

    def search(self, params=None):
        return self._request("GET", "products.json", params=params)

    def create(self, data):
        return self._request("POST", "products.json", data=data)

    def write(self, external_id, data):
        return self._request("PUT", f"products/{external_id}.json", data=data)

    def delete(self, external_id):
        return self._request("DELETE", f"products/{external_id}.json")
