import time
import json
import datetime
import requests
import traceback
from pathlib import Path
from web3 import Web3
from pycoingecko import CoinGeckoAPI

# DISCLAIMER: Use at your own risk. This interacts with real Ethereum mainnet.
# Never share your private key. Test with small amounts first.

## ----------- CONFIG START ----------- ##

vmu = 60
manual_max_term = 320
use_automatic_max_term = False

#only_claim_if_gas_is_below = 0.032
only_claim_if_gas_is_below = 0.042
#only_claim_if_gas_is_below = 0.052
max_priority_fee_per_gas = 0.005   # in gwei

claim_when_consecutive_count = 3
how_many_seconds_between_checks = 3

rpc_url = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID_HERE"

web3 = Web3(Web3.HTTPProvider(rpc_url))


your_wallet_address = '0x'
# ─── Load private key from pk2.txt ────────────────────────────────
PK_FILE = "pk2.txt"

try:
    pk_content = Path(PK_FILE).read_text(encoding="utf-8").strip()

    # Add 0x if someone forgot it
    if not pk_content.startswith("0x"):
        your_wallet_address_private_key = "0x" + pk_content
    else:
        your_wallet_address_private_key = pk_content

except FileNotFoundError:
    print(f"❌ Error: {PK_FILE} not found in the current directory!")
    exit(1)
except Exception as e:
    print(f"❌ Error reading {PK_FILE}: {e}")
    exit(1)

# Quick basic validation (not foolproof, but catches obvious mistakes)
pk_hex = your_wallet_address_private_key.removeprefix("0x")
if len(pk_hex) != 64 or not all(c in "0123456789abcdefABCDEF" for c in pk_hex):
    print("❌ Private key looks invalid (should be 64 hex chars)")
    exit(1)

print("Private key loaded successfully from pk2.txt ✓")
# Now you can use it normally
# account = web3.eth.account.from_key(your_wallet_address_private_key)


xenft_contract_address = web3.to_checksum_address('0x0a252663dbcc0b073063d6420a40319e438cfa59')
xen_public_address = web3.to_checksum_address('0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8')

# ────────────────────────────────────────────────
#  Real XENFT ABI (XENFT minting contract)
# ────────────────────────────────────────────────
xenft_abi = '''[
  {"inputs":[{"internalType":"address","name":"xenCrypto_","type":"address"},{"internalType":"uint256[]","name":"burnRates_","type":"uint256[]"},{"internalType":"uint256[]","name":"tokenLimits_","type":"uint256[]"},{"internalType":"uint256","name":"startBlockNumber_","type":"uint256"},{"internalType":"address","name":"forwarder_","type":"address"},{"internalType":"address","name":"royaltyReceiver_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
  {"inputs":[{"internalType":"address","name":"operator","type":"address"}],"name":"OperatorNotAllowed","type":"error"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"}],"name":"EndTorrent","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"address","name":"xenContract","type":"address"},{"indexed":true,"internalType":"address","name":"tokenContract","type":"address"},{"indexed":false,"internalType":"uint256","name":"xenAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokenAmount","type":"uint256"}],"name":"Redeemed","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"count","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"term","type":"uint256"}],"name":"StartTorrent","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},
  {"inputs":[],"name":"AUTHORS","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"BLACKOUT_TERM","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"COMMON_CATEGORY_COUNTER","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"LIMITED_CATEGORY_TIME_THRESHOLD","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"OPERATOR_FILTER_REGISTRY","outputs":[{"internalType":"contract IOperatorFilterRegistry","name":"","type":"address"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"POWER_GROUP_SIZE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"ROYALTY_BP","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"SPECIAL_CATEGORIES_VMU_THRESHOLD","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"trustedForwarder","type":"address"}],"name":"addForwarder","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"to","type":"address"}],"name":"bulkClaimMintReward","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"count","type":"uint256"},{"internalType":"uint256","name":"term","type":"uint256"}],"name":"bulkClaimRank","outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"count","type":"uint256"},{"internalType":"uint256","name":"term","type":"uint256"},{"internalType":"uint256","name":"burning","type":"uint256"}],"name":"bulkClaimRankLimited","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"burned","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"callClaimMintReward","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"term","type":"uint256"}],"name":"callClaimRank","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"genesisTs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"isApex","outputs":[{"internalType":"bool","name":"apex","type":"bool"}],"stateMutability":"pure","type":"function"},
  {"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"forwarder","type":"address"}],"name":"isTrustedForwarder","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"mintInfo","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"burned","type":"uint256"}],"name":"onTokenBurned","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"ownedTokens","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"powerDown","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"salePrice","type":"uint256"}],"name":"royaltyInfo","outputs":[{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"royaltyAmount","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"specialClassesBurnRates","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"specialClassesCounters","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"specialClassesTokenLimits","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"startBlockNumber","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"tokenIdCounter","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"vmuCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"xenBurned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"xenCrypto","outputs":[{"internalType":"contract XENCrypto","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]'''

# ────────────────────────────────────────────────
#  Real XEN Crypto ABI (the mint/rank/claim contract)
# ────────────────────────────────────────────────
xen_abi = '''[
  {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"rewardAmount","type":"uint256"}],"name":"MintClaimed","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"term","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"rank","type":"uint256"}],"name":"RankClaimed","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"term","type":"uint256"}],"name":"Staked","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},
  {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"reward","type":"uint256"}],"name":"Withdrawn","type":"event"},
  {"inputs":[],"name":"AUTHORS","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"DAYS_IN_YEAR","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"EAA_PM_START","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"EAA_PM_STEP","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"EAA_RANK_STEP","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"GENESIS_RANK","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"MAX_PENALTY_PCT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"MAX_TERM_END","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"MAX_TERM_START","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"MIN_TERM","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"REWARD_AMPLIFIER_END","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"REWARD_AMPLIFIER_START","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"SECONDS_IN_DAY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"TERM_AMPLIFIER","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"TERM_AMPLIFIER_THRESHOLD","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"WITHDRAWAL_WINDOW_DAYS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"XEN_APY_DAYS_STEP","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"XEN_APY_END","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"XEN_APY_START","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"XEN_MIN_BURN","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"XEN_MIN_STAKE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"activeMinters","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"activeStakes","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"claimMintReward","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"other","type":"address"},{"internalType":"uint256","name":"pct","type":"uint256"}],"name":"claimMintRewardAndShare","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"pct","type":"uint256"},{"internalType":"uint256","name":"term","type":"uint256"}],"name":"claimMintRewardAndStake","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"term","type":"uint256"}],"name":"claimRank","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"genesisTs","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"getCurrentAMP","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"getCurrentAPY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"getCurrentEAAR","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"getCurrentMaxTerm","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"rankDelta","type":"uint256"},{"internalType":"uint256","name":"amplifier","type":"uint256"},{"internalType":"uint256","name":"term","type":"uint256"},{"internalType":"uint256","name":"eaa","type":"uint256"}],"name":"getGrossReward","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},
  {"inputs":[],"name":"getUserMint","outputs":[{"components":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"term","type":"uint256"},{"internalType":"uint256","name":"maturityTs","type":"uint256"},{"internalType":"uint256","name":"rank","type":"uint256"},{"internalType":"uint256","name":"amplifier","type":"uint256"},{"internalType":"uint256","name":"eaaRate","type":"uint256"}],"internalType":"struct XENCrypto.MintInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"getUserStake","outputs":[{"components":[{"internalType":"uint256","name":"term","type":"uint256"},{"internalType":"uint256","name":"maturityTs","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"apy","type":"uint256"}],"internalType":"struct XENCrypto.StakeInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"globalRank","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"term","type":"uint256"}],"name":"stake","outputs":[],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"totalXenStaked","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
  {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"userBurns","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"userMints","outputs":[{"components":[{"internalType":"address","name":"user","type":"address"},{"internalType":"uint256","name":"term","type":"uint256"},{"internalType":"uint256","name":"maturityTs","type":"uint256"},{"internalType":"uint256","name":"rank","type":"uint256"},{"internalType":"uint256","name":"amplifier","type":"uint256"},{"internalType":"uint256","name":"eaaRate","type":"uint256"}],"internalType":"struct XENCrypto.MintInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
  {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"userStakes","outputs":[{"components":[{"internalType":"uint256","name":"term","type":"uint256"},{"internalType":"uint256","name":"maturityTs","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"apy","type":"uint256"}],"internalType":"struct XENCrypto.StakeInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}
]'''

## ------------ CONFIG END ------------ ##

## ----------- FUNCTIONS ----------- ##

def get_eth_usd_value():
    cg = CoinGeckoAPI()
    price = cg.get_price(ids=['ethereum'], vs_currencies='usd')
    return price['ethereum']['usd']

def get_timestamp():
    now = datetime.datetime.now()
    return f"{now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"

def fetch_current_max_term(xen_address):
    address = web3.to_checksum_address(xen_address)
    xen_contract = web3.eth.contract(address=address, abi=xen_abi)
    current_max_term = int(xen_contract.functions.getCurrentMaxTerm().call() / (60*60*24))
    return current_max_term

def get_gas_price():
    session = requests.Session()
    session.headers.update({'Content-Type':'application/json'})
    gas_price_data = session.post(
        url=rpc_url,
        json={"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
    )
    gas_price_gwei = int(gas_price_data.json()['result'], 16) / 1e9
    medium_gas_price_gwei = gas_price_gwei * 1.05
    return round(medium_gas_price_gwei, 3)

## ----------- MAIN LOGIC ----------- ##

if use_automatic_max_term:
    term = fetch_current_max_term(xen_public_address)
else:
    term = manual_max_term

print("------------------------------------------ XENFT CONFIGURATION ------------------------------------------")
print(f"VMU: {vmu}, TERM: {term}, Max Gas Fee (gwei): {only_claim_if_gas_is_below}, Max Priority Fee (gwei): {max_priority_fee_per_gas}")
print(f"Will attempt to mint {vmu} VMU × 1000 times when gas < {only_claim_if_gas_is_below} gwei for {claim_when_consecutive_count} consecutive checks")
print("---------------------------------------------------------------------------------------------------------")

time.sleep(how_many_seconds_between_checks)

contract = web3.eth.contract(address=xenft_contract_address, abi=xenft_abi)

MAX_MINT_ATTEMPTS = 1000
mint_attempts = 0
consecutive_count = 0

while mint_attempts < MAX_MINT_ATTEMPTS:
    try:
        maxFeePerGas = get_gas_price()

        if maxFeePerGas > only_claim_if_gas_is_below:
            consecutive_count = 0
            print(f"{get_timestamp()} - Waiting... Current: {maxFeePerGas} > {only_claim_if_gas_is_below}  |  Mint attempts: {mint_attempts}/{MAX_MINT_ATTEMPTS}")
            time.sleep(how_many_seconds_between_checks)
            continue

        consecutive_count += 1
        print(f"{get_timestamp()} - Test {consecutive_count}/{claim_when_consecutive_count} OK ({maxFeePerGas} gwei)  |  Mint attempts: {mint_attempts}/{MAX_MINT_ATTEMPTS}")

        if consecutive_count >= claim_when_consecutive_count:
            print(f"{get_timestamp()} - Gas low enough → attempting mint #{mint_attempts + 1} of {MAX_MINT_ATTEMPTS} ...")

            eth_cost_in_usd = get_eth_usd_value()
            balance_before_claim = round(float(web3.from_wei(web3.eth.get_balance(your_wallet_address), 'ether')), 6)
            total_account_value = round(eth_cost_in_usd * balance_before_claim, 2)

            effective_priority_gwei = min(max_priority_fee_per_gas, maxFeePerGas * 0.9)
            if effective_priority_gwei < max_priority_fee_per_gas:
                print(f"{get_timestamp()} - Priority fee capped to {effective_priority_gwei:.3f} gwei (was {max_priority_fee_per_gas})")

            tx = contract.functions.bulkClaimRank(vmu, term).build_transaction({
                'from': your_wallet_address,
                'nonce': web3.eth.get_transaction_count(your_wallet_address, 'pending'),
                'maxFeePerGas': web3.to_wei(maxFeePerGas, 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(effective_priority_gwei, 'gwei'),
                'chainId': web3.eth.chain_id,
            })

            # gas_estimate = web3.eth.estimate_gas(tx)
            # tx['gas'] = int(gas_estimate * 1.15)

            gas_estimate = web3.eth.estimate_gas(tx)
            tx['gas'] = min(int(gas_estimate * 1.20), 15_000_000)   # safer buffer + hard cap

            required_eth = tx['gas'] * tx['maxFeePerGas']
            if web3.eth.get_balance(your_wallet_address) < required_eth:
                print(f"CRITICAL: Insufficient ETH. Need at least {web3.from_wei(required_eth, 'ether'):.6f} ETH")
                print("Stopping script early.")
                break

            print(f"{get_timestamp()} - Balance before: {balance_before_claim} ETH (${total_account_value})")

            signed_tx = web3.eth.account.sign_transaction(tx, your_wallet_address_private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

            print(f"{get_timestamp()} - Tx submitted! Hash: {web3.to_hex(tx_hash)}")
            print(f"Etherscan: https://etherscan.io/tx/{web3.to_hex(tx_hash)}")

            gas_price_wei = web3.to_wei(maxFeePerGas, 'gwei')
            est_cost_wei = tx['gas'] * gas_price_wei
            cost_in_ether = float(round(web3.from_wei(est_cost_wei, 'ether'), 6))
            total_cost_usd = round(cost_in_ether * eth_cost_in_usd, 2)
            print(f"{get_timestamp()} - Expected cost: {cost_in_ether} ETH (~${total_cost_usd})")

            test_count = 0
            while round(float(web3.from_wei(web3.eth.get_balance(your_wallet_address), 'ether')), 6) == balance_before_claim:
                test_count += 1
                if test_count > 60:
                    print("→ No balance change after ~5 min → assuming failed / dropped")
                    break
                print(f"{get_timestamp()} - Waiting for confirmation... Test #{test_count}")
                time.sleep(how_many_seconds_between_checks + 10)

            balance_after_claim = round(float(web3.from_wei(web3.eth.get_balance(your_wallet_address), 'ether')), 6)
            total_cost = round(balance_before_claim - balance_after_claim, 6)
            total_cost_usd = round(total_cost * eth_cost_in_usd, 2)

            if total_cost > 0:
                per_vmu_cost = round(total_cost_usd / vmu, 2)
                print(f"{get_timestamp()} - Success! XENFT minted.")
                print(f"Actual cost: {total_cost} ETH (~${total_cost_usd}) → ${per_vmu_cost}/VMU")
            else:
                print(f"{get_timestamp()} - No ETH spent → transaction likely failed or reverted")

            print(f"New balance: {balance_after_claim} ETH (${round(eth_cost_in_usd * balance_after_claim, 2)})")
            print("───────────────────────────────────────────────")

            mint_attempts += 1
            consecutive_count = 0

            print(f"Mint attempts completed: {mint_attempts}/{MAX_MINT_ATTEMPTS}")

        time.sleep(how_many_seconds_between_checks)

    except Exception as e:
        print(f"{get_timestamp()} - ERROR during cycle: {e}")
        traceback.print_exc()
        consecutive_count = 0
        time.sleep(how_many_seconds_between_checks * 3)

print(f"\nScript finished after {mint_attempts} mint attempts (target was {MAX_MINT_ATTEMPTS}).")
print("Goodbye.")