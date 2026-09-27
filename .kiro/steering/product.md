# Product Overview

## What this is
A command-line automation bot that mints **XENFTs** (NFTs from the XEN Network) on
Ethereum mainnet, but only when network gas fees are low. It is a personal,
single-wallet tool run from the terminal.

## What it does
- Continuously polls the current gas price.
- When gas drops below a configured threshold for a set number of consecutive
  checks, it submits a `bulkClaimRank(vmu, term)` transaction to the XENFT
  contract, which mints a XENFT representing a batch of XEN "virtual mining
  units" (VMUs).
- Repeats up to a hard cap (`MAX_MINT_ATTEMPTS`, currently 1000), reporting the
  ETH/USD cost of each mint and the running attempt count.

## Why it exists
XENFT minting is only economical when gas is cheap. Watching gas manually and
firing transactions by hand is tedious and error-prone. This bot waits for the
right conditions and mints automatically, tracking real cost per VMU so the user
knows exactly what each mint is costing.

## Who uses it
The wallet owner only. It is not a multi-user service and has no UI beyond
terminal output. It signs transactions locally with a private key loaded from a
file.

## Key characteristics
- **Live-funds tool.** Every successful run spends real ETH on Ethereum mainnet.
- **Gas-gated.** Nothing is submitted unless gas is below the configured limit.
- **Cost-aware.** Reports estimated and actual cost in ETH and USD per mint and
  per VMU.
- **Fire-and-forget.** Designed to be left running; it self-throttles and retries
  on transient errors.

## Success criteria
- Mints only when gas is genuinely below threshold (no accidental high-fee mints).
- Never submits a transaction the wallet cannot afford.
- Clear, timestamped logging of every decision, submission, and outcome.

## Explicit non-goals
- Not a trading bot, portfolio manager, or financial-advice tool.
- Not a hosted service or shared product.
- No key custody beyond reading a local file the user controls.
