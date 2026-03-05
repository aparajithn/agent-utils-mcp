"""x402 payment middleware."""
import os
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse


class X402Middleware:
    """HTTP 402 payment middleware."""
    
    def __init__(self, wallet_address: str = None, price_per_request: float = 0.001):
        """
        Initialize x402 middleware.
        
        Args:
            wallet_address: Crypto wallet address for payments (if None, no paywall)
            price_per_request: Price per request in USD
        """
        self.wallet_address = wallet_address
        self.price_per_request = price_per_request
        self.enabled = wallet_address is not None
    
    def check_payment(self, request: Request) -> bool:
        """
        Check if request includes valid payment.
        
        For now, just checks for X-PAYMENT header presence.
        In production, this would verify the payment on-chain.
        """
        if not self.enabled:
            return True
        
        payment_header = request.headers.get("X-Payment")
        if payment_header:
            # In production: verify payment on-chain
            # For now: accept any payment header
            return True
        
        return False
    
    def create_payment_required_response(self) -> Response:
        """Create HTTP 402 Payment Required response."""
        return JSONResponse(
            status_code=402,
            content={
                "success": False,
                "error": "Payment required",
                "payment": {
                    "wallet_address": self.wallet_address,
                    "price_usd": self.price_per_request,
                    "currency": "USD",
                    "instructions": "Include X-Payment header with payment proof"
                }
            },
            headers={
                "X-Payment-Required": "true",
                "X-Payment-Address": self.wallet_address,
                "X-Payment-Amount": str(self.price_per_request)
            }
        )


# Initialize from environment
def get_x402_middleware() -> X402Middleware:
    """Get x402 middleware instance from environment."""
    wallet_address = os.getenv("X402_WALLET_ADDRESS")
    return X402Middleware(wallet_address=wallet_address)
