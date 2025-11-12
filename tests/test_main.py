import pytest
from unittest.mock import patch, Mock
from decimal import Decimal
from fastapi.testclient import TestClient
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, wei_to_eth

client = TestClient(app)


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    def test_root_endpoint(self):
        """Test that root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Ethereum Balance API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "health" in data["endpoints"]
        assert "balance" in data["endpoints"]


class TestWeiToEth:
    """Test cases for the wei_to_eth conversion function."""

    def test_wei_to_eth_zero(self):
        """Test conversion of zero wei."""
        result = wei_to_eth("0x0")
        assert result == Decimal("0")

    def test_wei_to_eth_one_wei(self):
        """Test conversion of 1 wei."""
        result = wei_to_eth("0x1")
        assert result == Decimal("0.000000000000000001")

    def test_wei_to_eth_one_ether(self):
        """Test conversion of 1 ether (10^18 wei)."""
        result = wei_to_eth("0xde0b6b3a7640000")  # 10^18 in hex
        assert result == Decimal("1.0")

    def test_wei_to_eth_large_amount(self):
        """Test conversion of large wei amount."""
        # 100 ETH = 100 * 10^18 wei
        wei_hex = hex(100 * 10**18)
        result = wei_to_eth(wei_hex)
        assert result == Decimal("100.0")

    def test_wei_to_eth_fractional(self):
        """Test conversion of fractional ether."""
        # 0.5 ETH = 5 * 10^17 wei
        wei_hex = hex(5 * 10**17)
        result = wei_to_eth(wei_hex)
        assert result == Decimal("0.5")


class TestBalanceEndpoint:
    """Test cases for the balance endpoint."""

    @patch('main.requests.post')
    def test_get_balance_success(self, mock_post):
        """Test successful balance retrieval."""
        # Mock Infura response
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": "0xde0b6b3a7640000",  # 1 ETH
            "id": 1
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        address = "0xc94770007dda54cF92009BFF0dE90c06F603a09f"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        # FastAPI serializes Decimal, check the numeric value
        assert Decimal(str(data["balance"])) == Decimal("1.0")
        mock_post.assert_called_once()

    @patch('main.requests.post')
    def test_get_balance_zero_balance(self, mock_post):
        """Test balance retrieval for address with zero balance."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": "0x0",
            "id": 1
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        address = "0x0000000000000000000000000000000000000000"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 200
        data = response.json()
        # FastAPI serializes Decimal, check the numeric value
        assert Decimal(str(data["balance"])) == Decimal("0")

    def test_get_balance_invalid_address_short(self):
        """Test balance endpoint with invalid short address."""
        address = "0x123"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid Ethereum address format" in data["detail"]

    def test_get_balance_invalid_address_no_prefix(self):
        """Test balance endpoint with address missing 0x prefix."""
        address = "c94770007dda54cF92009BFF0dE90c06F603a09f"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid Ethereum address format" in data["detail"]

    def test_get_balance_invalid_address_too_short(self):
        """Test balance endpoint with address that's too short."""
        address = "0x1234567890abcdef"  # Only 18 chars, needs 42
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid Ethereum address format" in data["detail"]

    @patch('main.requests.post')
    def test_get_balance_infura_error(self, mock_post):
        """Test balance endpoint when Infura returns an error."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": "execution reverted"
            },
            "id": 1
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        address = "0xc94770007dda54cF92009BFF0dE90c06F603a09f"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 502
        data = response.json()
        assert "Infura error" in data["detail"]

    @patch('main.requests.post')
    def test_get_balance_missing_result(self, mock_post):
        """Test balance endpoint when Infura response is missing result."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        address = "0xc94770007dda54cF92009BFF0dE90c06F603a09f"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 502
        data = response.json()
        assert "Unexpected response from Infura" in data["detail"]

    @patch('main.requests.post')
    def test_get_balance_request_exception(self, mock_post):
        """Test balance endpoint when request fails."""
        import requests
        mock_post.side_effect = requests.RequestException("Connection error")

        address = "0xc94770007dda54cF92009BFF0dE90c06F603a09f"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 502
        data = response.json()
        assert "Upstream request failed" in data["detail"]

    @patch('main.requests.post')
    def test_get_balance_http_error(self, mock_post):
        """Test balance endpoint when HTTP request returns error status."""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("HTTP 500")
        mock_post.return_value = mock_response

        address = "0xc94770007dda54cF92009BFF0dE90c06F603a09f"
        response = client.get(f"/address/balance/{address}")

        assert response.status_code == 502
        data = response.json()
        assert "Upstream request failed" in data["detail"]

    @patch('main.requests.post')
    def test_get_balance_payload_format(self, mock_post):
        """Test that the correct payload is sent to Infura."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": "0x0",
            "id": 1
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        address = "0xc94770007dda54cF92009BFF0dE90c06F603a09f"
        client.get(f"/address/balance/{address}")

        # Verify the payload sent to Infura
        call_args = mock_post.call_args
        assert call_args is not None
        payload = call_args.kwargs.get('json')
        assert payload["jsonrpc"] == "2.0"
        assert payload["method"] == "eth_getBalance"
        assert payload["params"] == [address, "latest"]
        assert payload["id"] == 1

