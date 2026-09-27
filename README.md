# XENFT Minter

A command-line bot that automatically mints **XENFTs** (from the [XEN Network](https://xen.network/)) on Ethereum mainnet — but only when gas fees are low. It watches the gas price and, once it drops below a threshold you set, submits a `bulkClaimRank` transaction to the XENFT contract. It repeats up to a hard cap and reports the ETH/USD cost of each mint.

> ⚠️ **This tool spends real ETH on Ethereum mainnet.** Every successful mint costs gas. Read the whole README before running it, and test with a wallet that holds only a small amount of ETH first.

---

## What you need before you start

You must supply **three things of your own**. The script will not work without them, and you should never use someone else's:

1. **Your own Infura RPC URL** — your connection to the Ethereum network.
2. **Your own wallet address** — the Ethereum address that will mint and pay the gas.
3. **Your own wallet private key** — required to sign transactions. This is placed in a file called `pk2.txt`.

These three are covered in detail in **[Configuration](#configuration)** below.

---

## Prerequisites

- **Python 3.9 or newer** — check with `python --version`.
- **pip** (comes with Python).
- A **funded Ethereum wallet** (a small amount of ETH to cover gas).
- An **Infura account** (free tier is fine).

---

## Installation

1. **Get the code** (clone the repo or download `XENFT.py`):
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>/"XENFT Minter"
   ```

2. **Install the Python dependencies:**
   ```bash
   pip install web3 requests pycoingecko
   ```
   (Optional but recommended: use a virtual environment first — `python -m venv venv` then activate it.)

---

## Configuration

Open `XENFT.py` in a text editor. All the settings live in the `CONFIG START` / `CONFIG END` block near the top.

### 1. Infura RPC URL (required — use your own)

Sign up for a free account at [infura.io](https://www.infura.io/), create a new API key/project, and copy your **Ethereum Mainnet** HTTPS endpoint. It looks like:

```
https://mainnet.infura.io/v3/YOUR_PROJECT_ID_HERE
```

Set it in the script:
```python
rpc_url = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID_HERE"
```

> Do **not** reuse the endpoint that ships in the file. Use your own — it's tied to your account and rate limits.

### 2. Wallet address (required — use your own)

```python
your_wallet_address = '0xYourWalletAddressHere'
```
This is the public address that will mint the XENFTs and pay for gas.

### 3. Private key (required — use your own, keep it secret)

The script reads your private key from a file named **`pk2.txt`** in the same folder as `XENFT.py`.

1. Copy the provided `pk2.txt.example` to a new file called `pk2.txt` in the `XENFT Minter` folder (or just create `pk2.txt` from scratch).
2. Paste **only** your wallet's private key into it (a 64-character hex string). A leading `0x` is optional.
3. Save it. Nothing else should be in the file.

> 🔐 **Never share your private key, commit it to git, or paste it anywhere online.** Anyone with it can drain your wallet. See [Security](#security) below.

### 4. Mint settings (tune to taste)

| Setting | Default | What it does |
|---|---|---|
| `vmu` | `60` | Virtual Mining Units per mint (higher = more XEN, more gas). |
| `manual_max_term` | `320` | Mint term length in days (used when auto term is off). |
| `use_automatic_max_term` | `False` | If `True`, fetches the current max term from the chain instead of using `manual_max_term`. |
| `only_claim_if_gas_is_below` | `0.042` | Only mint when gas (gwei) is below this. Lower = cheaper but less frequent. |
| `max_priority_fee_per_gas` | `0.005` | EIP-1559 priority (tip) fee in gwei. |
| `claim_when_consecutive_count` | `3` | Gas must be low this many checks in a row before minting. |
| `how_many_seconds_between_checks` | `3` | Seconds between gas checks. |
| `MAX_MINT_ATTEMPTS` | `1000` | Hard cap on total mints before the script stops. |

---

## Running it

From the `XENFT Minter` folder (with `pk2.txt` present):

```bash
python XENFT.py
```

You'll see a configuration summary, then the bot will start watching gas:

- While gas is too high, it prints `Waiting...` and keeps checking.
- Once gas is low enough for the required number of consecutive checks, it builds, signs, and submits a mint transaction.
- It prints the transaction hash, an Etherscan link, and the actual gas cost in ETH and USD after confirmation.
- It repeats until it hits `MAX_MINT_ATTEMPTS` or runs out of ETH.

To stop it at any time, press **Ctrl+C**.

---

## Safety features built in

- **Gas gating:** nothing is submitted unless gas is below your threshold for the required consecutive checks, and gas is re-checked right before submitting.
- **Affordability check:** the script aborts a mint if your wallet balance can't cover `gas × maxFeePerGas`, so it won't strand a failed transaction.
- **Cost reporting:** every mint reports estimated and actual cost in ETH and USD, plus cost per VMU.

---

## Security

- **`pk2.txt` holds your private key. Treat it like the keys to your house.**
- Add a `.gitignore` so you never commit it. At minimum:
  ```
  pk2.txt
  pk*.txt
  .env
  __pycache__/
  ```
- Consider using a **dedicated "hot" wallet** that holds only the ETH needed for gas, rather than your main wallet.
- Never paste your private key into a website, chat, or support ticket. No legitimate tool or person will ask for it.
- The Infura URL and wallet address are less sensitive than the private key, but still personal to you — keep them out of public commits where practical.

---

## Troubleshooting

| Symptom | Likely fix |
|---|---|
| `pk2.txt not found` | Create `pk2.txt` in the same folder as `XENFT.py`. |
| `Private key looks invalid` | It must be 64 hex characters (0x optional). No spaces or quotes. |
| `Insufficient ETH` | Add more ETH, or lower `vmu`. |
| Never mints | Your `only_claim_if_gas_is_below` may be lower than current gas — raise it, or wait for cheaper gas. |
| RPC / connection errors | Check your Infura URL is correct and your project is active. |
| `ModuleNotFoundError` | Run `pip install web3 requests pycoingecko`. |

---

## Disclaimer

This software is provided as-is, for educational purposes, with no warranty. It interacts with real funds on Ethereum mainnet. You are solely responsible for any transactions it makes and any ETH it spends. Use at your own risk, and always test with a small amount first.
