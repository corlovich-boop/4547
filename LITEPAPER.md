# 4547 Litepaper

**45 came first. 47 came back. 4547 begins.**

4547 is a mineable Scrypt cryptocurrency with a hard cap of 4,547 coins. It is a fork of Dogecoin Core 1.14.9, themed on the 45th and 47th presidencies. There is no premine. Mining opens on **Tuesday, October 27, 2026 at 12:00:00 UTC**, and the nodes reject blocks before that moment.

This paper explains what 4547 is, how coins are issued, how to mine it, and what could go wrong. It is a technical summary, not investment advice.

## 1. What 4547 is

- A proof-of-work coin using the Scrypt algorithm, the same one used by Litecoin and Dogecoin, so existing Scrypt miners and ASICs can mine it.
- A fork of Dogecoin Core 1.14.9 with its own genesis block, network magic, ports and address format. It shares no chain history with Dogecoin.
- A fixed supply of **4,547 coins**. Nothing was pre-mined and no coins were allocated to anyone at launch.
- The name is the two numbers it is built around, 45 and 47. They show up in the supply cap, the block rewards, the ports and the merge-mining chain ID.

## 2. Parameters

| | |
|---|---|
| Algorithm | Scrypt |
| Block time | 10 minutes |
| Maximum supply | 4,547 coins (about 4,533.6 are actually mined, see section 3) |
| Base block reward | 0.0495 coins |
| Launch ramp | Block n (n below 450) pays n/450 of the base reward, so the reward rises linearly from 0 to the full amount |
| Halving | Every 45,470 blocks (about 316 days) |
| Bonus block | Every block divisible by 4,547 pays 47 times the normal reward |
| Difficulty adjustment | LWMA-45, retargets every block |
| Coinbase maturity | 47 blocks |
| Network ports | P2P 4547, RPC 4545 |
| Addresses | Start with the digit 4 |
| Merge mining (AuxPoW) | Activates at block 4,547, chain ID 4547 |
| Genesis hash | `400cef90ca67f6a0f85d14d2ec3b1ade5acff17f02043c02f9733c413ee3a273` |
| Genesis message | "45 came first. 47 came back. 4547 begins." |

## 3. Supply and emission

Rewards start at zero and ramp up linearly over the first 450 blocks (about three days). Block 1 pays 1/450 of the full reward, block 225 pays half, and block 450 pays the full amount. This means there is no advantage to being a few minutes early at launch. After the ramp, each block pays 0.0495 coins. The reward halves every 45,470 blocks:

| Period | Blocks | Base reward per block |
|---|---|---|
| 1 | 0 to 45,469 | 0.0495 |
| 2 | 45,470 to 90,939 | 0.02475 |
| 3 | 90,940 to 136,409 | 0.012375 |
| and so on, halving each period | | |

**The 4547 Block.** Every block whose height is divisible by 4,547 pays 47 times the normal reward. The first one is block 4,547, about 31 days after launch. Each halving period contains 10 multiples of 4,547. In the first period one of them is the genesis block at height 0, which pays nothing, so only 9 bonus blocks pay out. These bonus blocks are part of the 4,547-coin cap. They are not extra supply.

The cap is slightly more than what is actually mined. The linear ramp at launch pays out about 11.2 coins less than full rewards would, and the genesis block's bonus is never paid, which is about 2.3 coins more. Together that leaves about 4,533.6 coins actually mined.

## 4. Merge mining (AuxPoW)

From block 4,547, 4547 accepts blocks that are mined as part of another Scrypt chain's work, so a miner can mine it at the same time as Litecoin or Dogecoin without giving up any hashrate. 4547's merge-mining chain ID is 4547.

Before block 4,547, miners work on 4547 directly. After it, both direct mining and merge mining work.

## 5. How to mine

- **Shared pool (PPLNS):** `stratum+tcp://pool.4547coin.net:3333`. 1% fee. Use your 4547 address as the username. Payouts are made after 55 confirmations.
- **Solo pool:** `stratum+tcp://pool.4547coin.net:3334`. 1% fee. Whoever finds a block gets the whole block reward, minus the fee.
- Any standard Scrypt miner works. The pools open at 12:00:00 UTC on October 27, 2026.

## 6. Wallets and source

- **Wallets:** Windows (64-bit) and Linux builds are on the release page: https://github.com/corlovich-boop/4547/releases/latest
- **Check the SHA256 sum** against the checksum files before you run anything.
- **Source code:** https://github.com/corlovich-boop/4547
- **Block explorer:** https://explorer.4547coin.net (live at launch)
- **Seeds:** `seed1.4547coin.net` and `seed2.4547coin.net` (port 4547)

## 7. Risks

This is experimental software and a brand-new network. Please read this section.

- **Low hashrate can mean reorganizations.** A new chain has very little proof of work behind it. Blocks in the first hours and days can be reorganized, and a large miner could attack a small chain. Wait for confirmations before you trust incoming coins. Merge mining is meant to help here, but it only starts at block 4,547.
- **Merge mining has been tested only at the node level.** The node's AuxPoW rules were tested on a private test network. They have not yet been tested against a real parent chain with live merge-mining software.
- **The software has not been independently audited.** It is a fork of Dogecoin Core with changes to consensus parameters, the difficulty algorithm and block rewards. Any of these could contain bugs.
- **Binaries are unsigned.** Windows may show a SmartScreen warning. Verify the SHA256 sum before running the wallet. If you prefer, build from the source on GitHub.
- **One developer.** The project is developed and operated by a single person, including the seeds, the pools and the explorer. These services can fail.
- **No promise of value.** Nothing here is a promise or a prediction about the price or the future of the coin. You may lose everything you put into it, including hardware and electricity spent mining.
- **Back up your wallet** and never share your `wallet.dat` file.

## 8. Disclaimer

4547 is experimental open-source software provided without warranty. It is not investment advice. It is not affiliated with or endorsed by any person, campaign, political party or government. References to presidential numbering are historical.

*Questions, bug reports and pool feedback are welcome on the Bitcointalk thread: https://bitcointalk.org/index.php?topic=5597340.0*
