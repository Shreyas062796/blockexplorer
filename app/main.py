# app/main.py
from decimal import Decimal
import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

INFURA_ENDPOINT = os.getenv(
    "INFURA_ENDPOINT",
    "https://mainnet.infura.io/v3/f3c095656381439aa1acb1722d9c62f2",
)

app = FastAPI(title="Ethereum Balance API")


@app.get("/")
async def root():
    return {
        "service": "Ethereum Balance API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "balance": "/address/balance/{address}",
        },
    }


class BalanceResponse(BaseModel):
    balance: Decimal


def wei_to_eth(wei_hex: str) -> Decimal:
    wei = int(wei_hex, 16)
    eth = Decimal(wei) / Decimal(10**18)
    return eth.quantize(Decimal("0.000000000000000001"))


@app.get("/address/balance/{address}", response_model=BalanceResponse)
def get_balance(address: str):
    # Basic address validation (length, 0x)
    if not (address.startswith("0x") and len(address) >= 42):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }

    try:
        resp = requests.post(INFURA_ENDPOINT, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Upstream request failed: {str(e)}"
        )

    data = resp.json()
    if "error" in data:
        raise HTTPException(status_code=502, detail=f"Infura error: {data['error']}")

    if "result" not in data:
        raise HTTPException(status_code=502, detail="Unexpected response from Infura")

    balance_wei_hex = data["result"]
    balance_eth = wei_to_eth(balance_wei_hex)
    return {"balance": balance_eth}
