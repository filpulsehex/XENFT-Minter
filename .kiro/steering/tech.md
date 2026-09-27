# Technology Stack

## Language & runtime
- **Python 3** (uses 3.9+ syntax such as `str.removeprefix`).
- Single-file script: `XENFT.py`. Run directly with `python XENFT.py`.

## Key libraries
- **web3.py** (`web3`) — Ethereum RPC, contract calls, EIP-1559 transaction
  building, local transaction signing.
- **requests** — direct JSON-RPC `eth_gasPrice` polling (separate from web3 for a
  lightweight gas check).
- **pycoingecko** (`CoinGeckoAPI`) — live ETH/USD price for cost reporting.
- Standard library: `time`, `json`, `datetime`, `traceback`, `pathlib`.

## External services
- **Ethereum mainnet** via an **Infura** HTTPS RPC endpoint (an Alchemy endpoint
  is present but commented out as a fallback).
- **CoinGecko API** for ETH price (no key required).

## On-chain contracts
- **XENFT** contract: `0x0a252663dbcc0b073063d6420a40319e438cfa59`
  - Primary call: `bulkClaimRank(count, term)` to mint.
- **XEN Crypto** contract: `0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8`
  - Used to read `getCurrentMaxTerm()` when automatic term selection is enabled.
- Full ABIs for both are embedded as JSON string literals in the script.

## Transaction model
- **EIP-1559** transactions: sets `maxFeePerGas` (from polled gas price × 1.05
  buffer) and `maxPriorityFeePerGas` (capped so priority never exceeds the max).
- Gas limit = `estimate_gas × 1.20`, hard-capped at 15,000,000.
- Pre-flight affordability check: aborts if wallet balance < `gas × maxFeePerGas`.
- Confirmation is detected by polling for a wallet balance change (up to ~5 min),
  not by receipt lookup.

## Configuration (edit constants at top of file)
- `vmu` — virtual mining units per mint.
- `manual_max_term` / `use_automatic_max_term` — term length in days, manual or
  fetched from chain.
- `only_claim_if_gas_is_below` — gas threshold in gwei.
- `max_priority_fee_per_gas` — priority fee in gwei.
- `claim_when_consecutive_count` — required consecutive low-gas checks.
- `how_many_seconds_between_checks` — poll interval.
- `MAX_MINT_ATTEMPTS` — hard cap on total mints (default 1000).

## Secrets & credentials
- Wallet **private key** is read from a local file named **`pk2.txt`** in the
  working directory (validated as 64 hex chars, `0x` optional).
- `your_wallet_address` and `rpc_url` are **placeholders** in the committed
  script: `your_wallet_address = '0x'` and the RPC URL ends in
  `YOUR_PROJECT_ID_HERE`. Each user fills in their own Infura project ID and
  wallet address before running (see `README.md`).
- Keep these as placeholders in anything committed to git — never commit a real
  Infura project ID, wallet address, or the `pk2.txt` private key. See
  `structure.md` for handling rules.

## Running
- Prerequisites: `pip install web3 requests pycoingecko`.
- Ensure `pk2.txt` exists in the same directory before running.
- `python XENFT.py` — runs an infinite gas-watch loop until the attempt cap or a
  fatal error (e.g. insufficient funds).

## Conventions for future changes
- Keep it a dependency-light, single-file script unless there's a strong reason to
  modularize.
- Preserve the gas-gating and affordability guards; never bypass them.
- Any new transaction path must keep the "re-check gas immediately before
  submitting" pattern.
