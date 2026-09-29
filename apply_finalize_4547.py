#!/usr/bin/env python3
"""
4547 finalization, run AFTER apply_4547.py, from the repo root:
    python3 apply_finalize_4547.py
  - binaries renamed: 4547d, 4547-cli, 4547-tx, 4547-qt
  - user-facing "Dogecoin" text -> "4547", own signed-message magic, own user agent
  - testnet and regtest become 4547 networks (own genesis, magic, ports, addresses)
  - DNS seeds seed1/seed2.4547coin.net (mainnet) and testseed1.4547coin.net (testnet)
Mainnet consensus is NOT touched: same genesis 400cef90...a273, same rules.
"""
import re, sys, pathlib

DOMAIN = "4547coin.net"
MAIN_HASH = "0x400cef90ca67f6a0f85d14d2ec3b1ade5acff17f02043c02f9733c413ee3a273"

def edit(path, old, new, count=1):
    p = pathlib.Path(path); s = p.read_text()
    n = s.count(old)
    if n != count:
        sys.exit(f"ABORT: {path}: expected {count} match(es), found {n} for:\n{old[:200]}")
    p.write_text(s.replace(old, new)); print(f"  ok  {path}")

def sub(path, pattern, repl, min_count=1):
    p = pathlib.Path(path); s = p.read_text()
    s2, n = re.subn(pattern, repl, s, flags=re.M)
    if n < min_count:
        sys.exit(f"ABORT: {path}: pattern not found: {pattern}")
    p.write_text(s2); print(f"  ok  {path}  ({n})")

cp = pathlib.Path("src/chainparams.cpp").read_text() if pathlib.Path("src/chainparams.cpp").exists() else ""
if MAIN_HASH not in cp:
    sys.exit("ABORT: run apply_4547.py first (4547 mainnet genesis not found).")
if "4547-cli" in pathlib.Path("configure.ac").read_text():
    sys.exit("Already applied.")

print("Binary names")
for old, new in (("dogecoind", "4547d"), ("dogecoin-qt", "4547-qt"),
                 ("dogecoin-cli", "4547-cli"), ("dogecoin-tx", "4547-tx")):
    edit("configure.ac", f"BITCOIN_{ {'dogecoind':'DAEMON','dogecoin-qt':'GUI','dogecoin-cli':'CLI','dogecoin-tx':'TX'}[old] }_NAME={old}".replace(" ", ""),
         f"BITCOIN_{ {'dogecoind':'DAEMON','dogecoin-qt':'GUI','dogecoin-cli':'CLI','dogecoin-tx':'TX'}[old] }_NAME={new}".replace(" ", ""))
edit("configure.ac",
     "AC_INIT([Dogecoin Core],[_CLIENT_VERSION_MAJOR._CLIENT_VERSION_MINOR._CLIENT_VERSION_REVISION],[https://github.com/dogecoin/dogecoin/issues],[dogecoin],[https://dogecoin.com/])",
     f"AC_INIT([4547 Core],[_CLIENT_VERSION_MAJOR._CLIENT_VERSION_MINOR._CLIENT_VERSION_REVISION],[https://github.com/corlovich-boop/4547/issues],[4547],[https://{DOMAIN}/])")
edit("configure.ac", "define(_COPYRIGHT_HOLDERS_SUBSTITUTION,[[Bitcoin Core and Dogecoin Core]])",
                     "define(_COPYRIGHT_HOLDERS_SUBSTITUTION,[[Bitcoin Core, Dogecoin Core and 4547]])")
NA = r"(?<![A-Za-z0-9])"   # not preceded by a letter/digit, so libdogecoin_* is left alone
sub("src/Makefile.am", NA + r"dogecoind(?![A-Za-z0-9-])", "4547d", 5)
sub("src/Makefile.am", NA + r"dogecoin-cli(?![A-Za-z0-9])", "4547-cli")
sub("src/Makefile.am", NA + r"dogecoin-tx(?![A-Za-z0-9])", "4547-tx")
sub("src/Makefile.am", NA + r"dogecoin_cli_", "4547_cli_", 5)
sub("src/Makefile.am", NA + r"dogecoin_tx_", "4547_tx_", 5)
sub("src/Makefile.qt.include", r"qt/dogecoin-qt", "qt/4547-qt", 2)
sub("src/Makefile.qt.include", r"qt_dogecoin_qt_", "qt_4547_qt_", 5)

print("User-facing text")
edit("src/validation.cpp", 'const std::string strMessageMagic = "Dogecoin Signed Message:\\n";',
                           'const std::string strMessageMagic = "4547 Signed Message:\\n";')
edit("src/clientversion.cpp", 'const std::string CLIENT_NAME("Shibetoshi");', 'const std::string CLIENT_NAME("4547");')
edit("src/util.cpp", 'const char * const BITCOIN_PID_FILENAME = "dogecoind.pid";',
                     'const char * const BITCOIN_PID_FILENAME = "4547d.pid";')
edit("src/rpc/server.cpp", 'return "> dogecoin-cli " + methodname', 'return "> 4547-cli " + methodname')
sub("src/bitcoind.cpp", r"dogecoind", "4547d", 2)
sub("src/bitcoind.cpp", r"dogecoin-cli", "4547-cli", 1)
sub("src/bitcoin-cli.cpp", r"dogecoin-cli", "4547-cli", 4)
# "Dogecoin" inside string literals only (comments and code untouched)
for f in ("src/init.cpp", "src/bitcoind.cpp", "src/net.cpp", "src/rpc/server.cpp", "src/rpc/rawtransaction.cpp",
          "src/rpc/mining.cpp", "src/rpc/misc.cpp", "src/rpc/blockchain.cpp", "src/wallet/rpcdump.cpp",
          "src/wallet/rpcwallet.cpp", "src/wallet/wallet.cpp", "src/bitcoin-cli.cpp", "src/bitcoin-tx.cpp"):
    p = pathlib.Path(f); s = p.read_text()
    s2, n = re.subn(r'"(?:[^"\\\n]|\\.)*"', lambda m: m.group(0).replace("Dogecoin", "4547"), s)
    p.write_text(s2); print(f"  ok  {f}")

print("DNS seeds (mainnet)")
MAIN_CLASS = re.search(r"class CMainParams.*?static CMainParams mainParams;", cp, re.S).group(0)
new_main = MAIN_CLASS.replace(
    "        vSeeds.clear();\n        vFixedSeeds.clear();\n",
    f'        vSeeds.clear();\n        vFixedSeeds.clear();\n'
    f'        vSeeds.push_back(CDNSSeedData("seed1.{DOMAIN}", "seed1.{DOMAIN}"));\n'
    f'        vSeeds.push_back(CDNSSeedData("seed2.{DOMAIN}", "seed2.{DOMAIN}"));\n', 1)
if new_main == MAIN_CLASS:
    sys.exit("ABORT: mainnet seed anchor not found")
cp = cp.replace(MAIN_CLASS, new_main)

def net_class(cls, var, nid, powlimit, bits, spacing, lwma, noretarget, auxpow_h, magic, port,
              gmsg, gtime, gnonce, ghash, gmerkle, pubkey, seeds, on_demand):
    seed_lines = "".join(f'        vSeeds.push_back(CDNSSeedData("{s}", "{s}"));\n' for s in seeds)
    m = ", ".join(f"0x{b:02x}" for b in magic)
    return f'''class {cls} : public CChainParams {{
private:
    Consensus::Params auxpowConsensus;
public:
    {cls}() {{
        strNetworkID = "{nid}";

        // Same 4547 emission rules as mainnet
        consensus.nSubsidyHalvingInterval = 45470;
        consensus.nSlowStartBlocks = 450;
        consensus.nBonusBlockInterval = 4547;
        consensus.nBonusBlockMultiplier = 47;
        consensus.fSimplifiedRewards = true;

        consensus.powLimit = uint256S("{powlimit}");
        consensus.nPowTargetSpacing = {spacing};
        consensus.nPowTargetTimespan = {spacing};
        consensus.nLwmaWindow = {lwma};
        consensus.fDigishieldDifficultyCalculation = false;
        consensus.fPowAllowMinDifficultyBlocks = false;
        consensus.fPowAllowDigishieldMinDifficultyBlocks = false;
        consensus.fPowNoRetargeting = {noretarget};
        consensus.nCoinbaseMaturity = 47;

        consensus.nMajorityEnforceBlockUpgrade = 51;
        consensus.nMajorityRejectBlockOutdated = 75;
        consensus.nMajorityWindow = 100;
        consensus.BIP34Height = 1;
        consensus.BIP34Hash = uint256();
        consensus.BIP65Height = 1;
        consensus.BIP66Height = 1;
        consensus.nRuleChangeActivationThreshold = 108;
        consensus.nMinerConfirmationWindow = 144;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].bit = 28;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].nStartTime = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].nTimeout = 999999999999ULL;
        consensus.vDeployments[Consensus::DEPLOYMENT_CSV].bit = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_CSV].nStartTime = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_CSV].nTimeout = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_SEGWIT].bit = 1;
        consensus.vDeployments[Consensus::DEPLOYMENT_SEGWIT].nStartTime = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_SEGWIT].nTimeout = 0;
        consensus.nMinimumChainWork = uint256S("0x00");
        consensus.defaultAssumeValid = uint256S("0x00");

        // AuxPoW (merge mining) switches on at block {auxpow_h} on this network
        consensus.nAuxpowChainId = 0x11C3;
        consensus.fStrictChainId = true;
        consensus.fAllowLegacyBlocks = true;
        consensus.nHeightEffective = 0;
        auxpowConsensus = consensus;
        auxpowConsensus.nHeightEffective = {auxpow_h};
        auxpowConsensus.fAllowLegacyBlocks = false;
        auxpowConsensus.pLeft = nullptr;
        auxpowConsensus.pRight = nullptr;
        consensus.pRight = &auxpowConsensus;
        pConsensusRoot = &consensus;

        pchMessageStart[0] = 0x{magic[0]:02x};
        pchMessageStart[1] = 0x{magic[1]:02x};
        pchMessageStart[2] = 0x{magic[2]:02x};
        pchMessageStart[3] = 0x{magic[3]:02x};
        nDefaultPort = {port};
        nPruneAfterHeight = 1000;

        const char* pszTimestamp = "{gmsg}";
        const CScript genesisOutputScript = CScript() << OP_RETURN;
        genesis = CreateGenesisBlock(pszTimestamp, genesisOutputScript, {gtime}, {gnonce}, {bits}, 1, 0);
        consensus.hashGenesisBlock = genesis.GetHash();
        auxpowConsensus.hashGenesisBlock = consensus.hashGenesisBlock;
        assert(consensus.hashGenesisBlock == uint256S("{ghash}"));
        assert(genesis.hashMerkleRoot == uint256S("{gmerkle}"));

        vSeeds.clear();
        vFixedSeeds.clear();
{seed_lines}
        base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,{pubkey});
        base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,196);
        base58Prefixes[SECRET_KEY] =     std::vector<unsigned char>(1,239);
        base58Prefixes[EXT_PUBLIC_KEY] = boost::assign::list_of(0x04)(0x35)(0x87)(0xCF).convert_to_container<std::vector<unsigned char> >();
        base58Prefixes[EXT_SECRET_KEY] = boost::assign::list_of(0x04)(0x35)(0x83)(0x94).convert_to_container<std::vector<unsigned char> >();

        fMiningRequiresPeers = false;
        fDefaultConsistencyChecks = {on_demand};
        fRequireStandard = false;
        fMineBlocksOnDemand = {on_demand};

        checkpointData = (CCheckpointData) {{
            boost::assign::map_list_of
            ( 0, uint256S("{ghash}"))
        }};
        chainTxData = ChainTxData{{ {gtime}, 0, 0 }};
    }}

    void UpdateBIP9Parameters(Consensus::DeploymentPos d, int64_t nStartTime, int64_t nTimeout)
    {{
        consensus.vDeployments[d].nStartTime = nStartTime;
        consensus.vDeployments[d].nTimeout = nTimeout;
    }}
}};
static {cls} {var};
'''

print("Testnet -> 4547 testnet")
TEST = net_class("CTestNetParams", "testNetParams", "test",
    "0x000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "0x1f0fffff",
    "10 * 60", 45, "false", 45, (0x34, 0x35, 0x34, 0x37), 14547,
    "4547 testnet - 45 came first. 47 came back.", 1790208000, 3637,
    "0x66f73c8787a7907858fbfa28266c8077f588f564f249301a8b72ee150e0450e2",
    "0x8078a5ba8cc40c8396568a8fabf69f2c34aa00d5ed6f3a53a59f4c4dda7a796e",
    127, [f"testseed1.{DOMAIN}"], "false")
cp, n = re.subn(r"class CTestNetParams : public CChainParams \{.*?\nstatic CTestNetParams testNetParams;\n", lambda m: TEST, cp, flags=re.S)
if n != 1: sys.exit("ABORT: testnet class not found")

print("Regtest -> 4547 regtest")
REG = net_class("CRegTestParams", "regTestParams", "regtest",
    "0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "0x207fffff",
    "10 * 60", 45, "true", 45, (0x52, 0x34, 0x35, 0x37), 18547,
    "4547 regtest", 1790208000, 2,
    "0xb256b7027f4aff043deb4554c26e759f61cf8e21c4414ee055d3efa7f8cff59f",
    "0x494ab230aa3ff8ce684b2520141ac45e1c501d6174b1e1acf9574ba2122a5c07",
    122, [], "true")
cp, n = re.subn(r"class CRegTestParams : public CChainParams \{.*?\nstatic CRegTestParams regTestParams;\n", lambda m: REG, cp, flags=re.S)
if n != 1: sys.exit("ABORT: regtest class not found")
pathlib.Path("src/chainparams.cpp").write_text(cp); print("  ok  src/chainparams.cpp")

edit("src/chainparamsbase.cpp", "        nRPCPort = 44555;", "        nRPCPort = 14545;")
edit("src/chainparamsbase.cpp", "        nRPCPort = 18332;", "        nRPCPort = 18545;")
edit("src/chainparamsbase.cpp", 'strDataDir = "testnet3";', 'strDataDir = "testnet";')

print("\nDone. 4547 finalized. Rebuild with ./autogen.sh && ./configure ... && make")
