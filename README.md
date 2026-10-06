# 4547

**45 came first. 47 came back. 4547 begins.**

4547 is a mineable Scrypt coin with a hard cap of **4,547 coins**. It is a fork of Dogecoin Core 1.14.9 (MIT license), with every consensus parameter built from the numbers 45 and 47, for the 45th and 47th US presidencies.

- Website: https://4547coin.net
- Explorer: https://explorer.4547coin.net (live after launch)
- **Mining opens Tuesday, October 27, 2026 at 12:00:00 UTC**

> 4547 is experimental open-source software provided as is, with no warranty. Nothing here is investment advice or a promise of value. 4547 is not affiliated with, endorsed by, or connected to any person, campaign, political party, or government. References to presidential numbering are historical.

## Parameters

| | |
|---|---|
| Algorithm | Scrypt (N=1024, r=1, p=1) |
| Block time | 10 minutes |
| Max supply | 4,547 (about 4,533.6 actually mined, because of the launch ramp) |
| Block reward | 0.0495 (reached after a 450-block launch ramp; early blocks pay tiny amounts) |
| 4547 Block | every block divisible by 4,547 pays 47x the normal reward |
| Halving | every 45,470 blocks (about 316 days) |
| Difficulty | LWMA-45, retargets every block over a 45-block window |
| Coinbase maturity | 47 blocks |
| Merge mining (AuxPoW) | switches on at block 4,547, chain ID 4547 (0x11C3) |
| Ports | P2P 4547, RPC 4545 (testnet 14547/14545, regtest 18547/18545) |
| Address prefix | addresses start with `4` |
| Network magic | 0x45 0x47 0x45 0x47 |
| Premine | none |

Genesis hash: `400cef90ca67f6a0f85d14d2ec3b1ade5acff17f02043c02f9733c413ee3a273`
Genesis message: `45 came first. 47 came back. 4547 begins.`

The genesis timestamp is 12:22:30 UTC on launch day, which is exactly the 1,350 s future-time limit, so nodes first accept a block at 12:00:00 UTC. Blocks in the first hour can still be re-organized, so wait for confirmations before trusting early coins.

## Wallets

Download from the [Releases page](RELEASE_LINK_HERE) and **check the SHA256 sum** against `SHA256SUMS-*.txt` before running anything.

**Windows (64-bit):** unzip `4547-wallet-win64-861063e66.zip` anywhere and run the Qt wallet. Windows SmartScreen may warn about an unrecognized app because the binaries are not code-signed; verify the checksum, then choose "More info" then "Run anyway". Data lives in `%APPDATA%\4547`.

**Linux (x86_64):** unpack `4547-wallet-linux-x86_64-861063e66.tar.gz`. It contains `4547d` and `4547-cli` (headless node and RPC client).

Back up your `wallet.dat` and keep it somewhere safe. Nobody can recover your coins for you.

## Run a node

```
4547d -daemon
4547-cli getblockcount
```

Seeds are built in: `seed1.4547coin.net` and `seed2.4547coin.net` (port 4547). To add one by hand: `addnode=seed1.4547coin.net:4547` in `4547.conf`.

## Mining

Mine with any Scrypt ASIC (the same hardware that mines Litecoin and Dogecoin).

- Shared pool (PPLNS): `stratum+tcp://STRATUM_ADDRESS:3333` (1% fee, payouts after 55 confirmations)
- Solo pool: `stratum+tcp://STRATUM_ADDRESS:3334` (1% fee, whoever finds a block gets the whole reward)
- Username: your 4547 address (starts with `4`), optionally `.workername`
- Password: anything

You can also solo mine against your own node through `getblocktemplate`.

## Build from source

Standard Dogecoin Core 1.14.x build process:

```
git clone https://github.com/corlovich-boop/4547
cd 4547
./autogen.sh
./configure --without-gui --disable-tests --disable-bench --with-incompatible-bdb
make -j$(nproc)
```

Verify the chain yourself:

```
4547-cli getblockhash 0
4547-cli getblock $(4547-cli getblockhash 0) 2
```

## License

MIT. Built on Dogecoin Core and Bitcoin Core.
