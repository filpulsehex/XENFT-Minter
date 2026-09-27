# Project Structure

## Current layout
```
XENFT Minter/
├── XENFT.py          # The entire bot: config, ABIs, helpers, main loop
├── pk2.txt           # Wallet private key (MUST exist at runtime; never commit)
└── .kiro/
    └── steering/     # These steering docs
```

`XENFT.py` is intentionally a single file with clearly marked sections:
1. **CONFIG START/END** — tunable constants (gas thresholds, VMU, term, timings).
2. **Contract addresses + embedded ABIs** — XENFT and XEN Crypto JSON ABIs.
3. **FUNCTIONS** — helpers: `get_eth_usd_value`, `get_timestamp`,
   `fetch_current_max_term`, `get_gas_price`.
4. **MAIN LOGIC** — the gas-watch `while` loop that builds, signs, submits, and
   confirms mint transactions.

## Runtime expectations
- Working directory must contain `pk2.txt` (the script exits immediately if it is
  missing or malformed).
- Network access to the Infura RPC endpoint and CoinGecko is required.

## Security & secret-handling rules (important)
- **Never commit `pk2.txt`.** It holds a raw private key controlling real funds.
- **Never print, log, or echo the private key** or its file contents beyond the
  existing "loaded successfully" confirmation.
- The committed script ships with **placeholders**: `your_wallet_address = '0x'`
  and an RPC URL ending in `YOUR_PROJECT_ID_HERE`. Keep them as placeholders in
  git — never replace them with a real Infura project ID or wallet address in a
  committed version. Users supply their own locally per the `README.md`.
- Prefer moving the RPC URL and wallet address to environment variables or a
  local, git-ignored config file in future edits rather than hardcoding real
  values.
- Recommend adding a `.gitignore` that excludes `pk2.txt`, any `pk*.txt`, and any
  `.env` file. If asked to initialize git here, create that `.gitignore` first.

## Coding conventions
- Keep tunables in the CONFIG block at the top; do not scatter magic numbers
  through the main loop.
- Preserve timestamped `print` logging for every meaningful step (waiting,
  gas OK, submitting, confirming, result).
- Preserve the safety guards in this order before any submission:
  1. Gas below threshold for the required consecutive checks.
  2. EIP-1559 fees computed with buffer; priority fee capped below max.
  3. Affordability check (balance ≥ gas × maxFeePerGas) — abort if it fails.
- On transient errors, log with `traceback`, reset `consecutive_count`, back off,
  and continue; only `break` on unrecoverable conditions (e.g. insufficient ETH).

## When extending
- New features (e.g. multi-wallet, alternate contracts, notifications) should slot
  into the existing section structure or, if large, be factored into small modules
  imported by `XENFT.py` — but keep the "single obvious entry point" feel.
- Any change touching transaction submission must keep the live gas re-check and
  the affordability guard intact.
