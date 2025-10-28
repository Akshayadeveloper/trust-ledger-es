
import json
import hashlib
import time
from typing import Dict, Any, List, Optional

class EventBlock:
    """Represents a single immutable domain event/block in the ledger."""
    def __init__(self, event_type: str, payload: Dict[str, Any], previous_hash: str):
        self.timestamp = int(time.time())
        self.event_type = event_type
        self.payload = payload
        self.previous_hash = previous_hash
        self.block_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculates a unique, deterministic hash for this block's content."""
        # The inclusion of previous_hash makes this a chain
        data_to_hash = {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash
        }
        canonical_string = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Returns a serializable dictionary representation of the block."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "block_hash": self.block_hash
        }


class TrustLedger:
    """The immutable chain of events."""
    def __init__(self):
        # Start with a "Genesis" block
        self.chain: List[EventBlock] = [self._create_genesis_block()]

    def _create_genesis_block(self) -> EventBlock:
        """The starting point of the chain."""
        return EventBlock(
            event_type="GENESIS",
            payload={"message": "Ledger initialized"},
            previous_hash="0" * 64
        )

    def add_event(self, event_type: str, payload: Dict[str, Any]) -> EventBlock:
        """Creates a new event block and links it to the chain."""
        latest_block = self.chain[-1]
        new_block = EventBlock(
            event_type=event_type,
            payload=payload,
            previous_hash=latest_block.block_hash
        )
        self.chain.append(new_block)
        print(f"✅ Event Added: {event_type}. Hash: {new_block.block_hash[:10]}...")
        return new_block

    def validate_chain(self) -> bool:
        """Verifies the integrity of the entire chain by re-calculating hashes."""
        print("\n--- Running Chain Validation ---")
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # 1. Check Previous Hash Link
            if current_block.previous_hash != previous_block.block_hash:
                print(f"🚨 INTEGRITY FAILED at Block {i}: Previous hash mismatch!")
                return False
            
            # 2. Check Self Hash Integrity (using a temporary object to avoid re-hashing the original)
            temp_block = EventBlock(current_block.event_type, current_block.payload, current_block.previous_hash)
            if temp_block.block_hash != current_block.block_hash:
                print(f"🚨 INTEGRITY FAILED at Block {i}: Self-hash calculation mismatch!")
                return False
                
        print("✅ Chain integrity verified.")
        return True

# --- Demonstration ---

ledger = TrustLedger()

# Add domain events for a banking transaction
ledger.add_event(
    event_type="ACCOUNT_CREATED",
    payload={"account_id": "U456", "initial_balance": 0.0}
)
ledger.add_event(
    event_type="DEPOSIT_MADE",
    payload={"account_id": "U456", "amount": 100.0, "source": "ATM"}
)
ledger.add_event(
    event_type="WITHDRAWAL_ATTEMPT",
    payload={"account_id": "U456", "amount": 50.0, "success": True}
)

ledger.validate_chain()

# Simulate a tamper attempt (e.g., changing the payload of an old event)
print("\n--- Simulating Tamper Attempt on DEPOSIT_MADE event ---")
# Warning: Do not do this in a real Event Sourcing system!
ledger.chain[2].payload["amount"] = 50000.0 # Change $100 to $50,000

# The chain is now broken because the tampered block's hash no longer matches 
# the 'previous_hash' stored in the next block (Block 3).
ledger.validate_chain()
      
