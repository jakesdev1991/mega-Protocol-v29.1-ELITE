# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import json
import asyncio
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.transaction import Transaction

# Paths
WALLET_PATH = os.path.expanduser("~/.config/solana/id.json")
RPC_URL = "https://api.devnet.solana.com" # Should be replaced with Helius/QuickNode

class SolanaExecutor:
    def __init__(self, simulate=True):
        self.keypair = self._load_keypair()
        self.simulate = simulate
        mode_str = "SIMULATION" if self.simulate else "LIVE"
        print(f"🛠️  Executor initialized ({mode_str}) with Pubkey: {self.keypair.pubkey()}")

    def _load_keypair(self):
        with open(WALLET_PATH, "r") as f:
            secret = bytes(json.loads(f.read()))
        return Keypair.from_bytes(secret)

    async def get_balance(self):
        if self.simulate:
            print("💰 Current Balance: 2.0 SOL (SIMULATED)")
            return 2.0
        
        from solana.rpc.commitment import Confirmed
        async with AsyncClient(RPC_URL) as client:
            res = await client.get_balance(self.keypair.pubkey(), commitment=Confirmed)
            balance = res.value / 1e9
            print(f"💰 Current Balance: {balance} SOL (Commitment: Confirmed)")
            return balance

    async def request_airdrop(self, amount_sol=2.0):
        """Requests an airdrop and waits for confirmation."""
        if self.simulate:
            print(f"💧 Simulated {amount_sol} SOL airdrop confirmed.")
            return True

        from solana.rpc.commitment import Confirmed
        print(f"💧 Requesting {amount_sol} SOL airdrop for {self.keypair.pubkey()}...")
        async with AsyncClient(RPC_URL) as client:
            try:
                # Request airdrop (lamports)
                signature = (await client.request_airdrop(
                    self.keypair.pubkey(), 
                    int(amount_sol * 1e9)
                )).value
                
                print(f"📝 Airdrop sent. Tx: {signature}. Waiting for confirmation...")
                
                # Wait for confirmation
                await client.confirm_transaction(signature, commitment=Confirmed)
                print("✅ Airdrop confirmed!")
                await self.get_balance()
                return True
            except Exception as e:
                print(f"⚠️ Airdrop failed: {e}")
                return False

    async def execute_mock_swap(self, amount_sol=0.1):
        """
        Constructs and signs an actual self-transfer transaction 
        to verify the 'firing sequence' on-chain.
        """
        if self.simulate:
            import random
            fake_sig = f"SIM_{random.getrandbits(128):x}"
            print(f"🚀 [Simulated Fire] Signed and broadcasted {amount_sol:.4f} SOL transfer.")
            print(f"✅ Transaction broadcasted! Signature: {fake_sig}")
            return {"status": "SUCCESS", "signature": fake_sig}

        print(f"🚀 [Firing Sequence] Initiating real on-chain self-transfer of {amount_sol} SOL...")
        
        from solana.rpc.async_api import AsyncClient
        from solders.system_program import TransferParams, transfer
        from solders.message import MessageV0
        from solders.transaction import VersionedTransaction

        async with AsyncClient(RPC_URL) as client:
            try:
                # 1. Fetch latest blockhash
                recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
                
                # 2. Create instruction (Self-transfer)
                # Note: This will fail if balance is 0, but the logic is now real.
                ix = transfer(TransferParams(
                    from_pubkey=self.keypair.pubkey(),
                    to_pubkey=self.keypair.pubkey(),
                    lamports=int(amount_sol * 1e9)
                ))
                
                # 3. Compile Message
                msg = MessageV0.try_compile(
                    payer=self.keypair.pubkey(),
                    instructions=[ix],
                    address_lookup_table_accounts=[],
                    recent_blockhash=recent_blockhash
                )
                
                # 4. Sign Transaction
                tx = VersionedTransaction(msg, [self.keypair])
                
                # 5. Broadcast
                print("📝 Signing and broadcasting transaction...")
                res = await client.send_transaction(tx)
                print(f"✅ Transaction broadcasted! Signature: {res.value}")
                
                return {
                    "timestamp": "2026-04-18T00:00:00Z",
                    "action": "SOL_SELF_TRANSFER",
                    "signature": str(res.value),
                    "status": "SUCCESS"
                }
            except Exception as e:
                print(f"❌ Transaction failed: {e}")
                return {"status": "FAILED", "error": str(e)}

if __name__ == "__main__":
    executor = SolanaExecutor()
    asyncio.run(executor.get_balance())
