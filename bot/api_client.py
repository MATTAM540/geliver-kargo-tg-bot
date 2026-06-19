import httpx
from bot.config import GELIVER_API_TOKEN, GELIVER_ORGANIZATION_ID, GELIVER_BASE_URL


class GeliverAPI:
    def __init__(self):
        self.base_url = GELIVER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {GELIVER_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        client = await self._get_client()
        url = f"{self.base_url}/{path}"
        response = await client.request(method, url, headers=self.headers, **kwargs)
        return response.json()

    async def _get(self, path: str, params: dict = None) -> dict:
        return await self._request("GET", path, params=params)

    async def _post(self, path: str, data: dict = None) -> dict:
        return await self._request("POST", path, json=data)

    async def _delete(self, path: str) -> dict:
        return await self._request("DELETE", path)

    # ── Fiyat Sorgulama ──

    async def get_prices(
        self, length: float, width: float, height: float, weight: float
    ) -> dict:
        params = {
            "paramType": "parcel",
            "length": length,
            "width": width,
            "height": height,
            "weight": weight,
            "organizationId": GELIVER_ORGANIZATION_ID,
        }
        return await self._get("priceList", params=params)

    # ── Şehir & İlçe ──

    async def get_cities(self) -> dict:
        return await self._get("cities")

    async def get_districts(self, city_code: str) -> dict:
        return await self._get("districts", params={"cityCode": city_code})

    # ── Adres Yönetimi ──

    async def get_addresses(self, page: int = 1, limit: int = 10) -> dict:
        return await self._get("addresses", params={"page": page, "limit": limit})

    async def create_address(self, address_data: dict) -> dict:
        return await self._post("addresses", data=address_data)

    async def delete_address(self, address_id: str) -> dict:
        return await self._delete(f"addresses/{address_id}")

    # ── Gönderi (Kargo) Yönetimi ──

    async def get_shipments(self, page: int = 1, limit: int = 10) -> dict:
        return await self._get("shipments", params={"page": page, "limit": limit})

    async def create_shipment(self, shipment_data: dict) -> dict:
        return await self._post("shipments", data=shipment_data)

    async def cancel_shipment(self, shipment_id: str) -> dict:
        return await self._delete(f"shipments/{shipment_id}")

    async def return_shipment(self, shipment_id: str) -> dict:
        return await self._post("returnShipment", data={"shipmentId": shipment_id})

    # ── Webhook Yönetimi ──

    async def get_webhooks(self) -> dict:
        return await self._get("webhook")

    async def create_webhook(self, webhook_data: dict) -> dict:
        return await self._post("webhook", data=webhook_data)

    async def delete_webhook(self, webhook_id: str) -> dict:
        return await self._delete(f"webhook/{webhook_id}")

    async def test_webhook(self) -> dict:
        return await self._post("webhook/test")


api = GeliverAPI()
