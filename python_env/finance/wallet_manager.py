# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
from solders.keypair import Keypair
from solana.rpc.api import Client

WALLET_PATH = os.path.expanduser("~/.config/solana/id.json")

def initialize_wallet():
    """Generates a new keypair if it doesn't exist and returns the public key."""
    if not os.path.exists(WALLET_PATH):
        print("🔑 No wallet found. Generating new Devnet keypair...")
        os.makedirs(os.path.dirname(WALLET_PATH), exist_ok=True)
        keypair = Keypair()
        with open(WALLET_PATH, "w") as f:
            f.write(str(list(keypair.to_bytes())))
        print(f"✅ Wallet generated and saved to {WALLET_PATH}")
    else:
        with open(WALLET_PATH, "r") as f:
            secret = bytes(json.loads(f.read()))
            keypair = Keypair.from_bytes(secret)
        print(f"✅ Wallet loaded from {WALLET_PATH}")
        
    print(f"🛰️  Public Key: {keypair.pubkey()}")
    return keypair

def get_airdrop(pubkey):
    """Requests 2 fake SOL from the Devnet faucet."""
    print(f"💧 Requesting airdrop for {pubkey}...")
    client = Client("https://api.devnet.solana.com")
    try:
        # 2 SOL in lamports
        res = client.request_airdrop(pubkey, 2000000000)
        print(f"✅ Airdrop requested. Tx: {res.value}")
    except Exception as e:
        print(f"⚠️ Airdrop failed (rate limited?): {e}")

if __name__ == "__main__":
    kp = initialize_wallet()
    get_airdrop(kp.pubkey())
