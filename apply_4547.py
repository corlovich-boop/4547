#!/usr/bin/env python3
"""
Applies the 4547 consensus changes to a Dogecoin Core v1.14.9 checkout.
Run from the repo root:  python3 apply_4547.py
Every edit is an exact match; if anything doesn't match, it stops and changes nothing further.
"""
import re, sys, pathlib

GENESIS_MSG   = "45 came first. 47 came back. 4547 begins."
GENESIS_TIME  = 1793103750
GENESIS_NONCE = 88204
GENESIS_HASH  = "0x400cef90ca67f6a0f85d14d2ec3b1ade5acff17f02043c02f9733c413ee3a273"
GENESIS_MERKLE= "0xf052a2c5a763af37e569623b9a20b04f43b6f6bc1cc07bbdb5c8ccb4911d2632"

def edit(path, old, new, count=1):
    p = pathlib.Path(path); s = p.read_text()
    n = s.count(old)
    if n != count:
        sys.exit(f"ABORT: {path}: expected {count} match(es), found {n} for:\n{old[:200]}")
    p.write_text(s.replace(old, new))
    print(f"  ok  {path}")

def edit_re(path, pattern, new):
    p = pathlib.Path(path); s = p.read_text()
    s2, n = re.subn(pattern, lambda m: new, s, count=1, flags=re.S)
    if n != 1:
        sys.exit(f"ABORT: {path}: pattern not found: {pattern[:120]}")
    p.write_text(s2); print(f"  ok  {path}")

if not pathlib.Path("src/dogecoin.cpp").exists():
    sys.exit("Run this from the root of the Dogecoin Core checkout.")
if "4547" in pathlib.Path("src/amount.h").read_text():
    sys.exit("Already applied.")

print("Supply cap")
edit("src/amount.h",
     "static const CAmount MAX_MONEY = 10000000000 * COIN; // Dogecoin: maximum of 100B coins (given some randomness), max transaction 10,000,000,000",
     "static const CAmount MAX_MONEY = 4547 * COIN; // 4547: hard cap of 4,547 coins")

print("Consensus params")
edit("src/consensus/params.h",
     "    /** Height-aware consensus parameters */",
     "    /** 4547 parameters (0 = disabled, so testnet/regtest keep Dogecoin behaviour) */\n"
     "    int nSlowStartBlocks = 0;       // reward ramps linearly from 0 over this many blocks\n"
     "    int nBonusBlockInterval = 0;    // every Nth block is a bonus block (4547)\n"
     "    int nBonusBlockMultiplier = 1;  // bonus block pays this multiple of the normal reward (47)\n"
     "    int64_t nLwmaWindow = 0;        // LWMA difficulty averaging window in blocks (45)\n\n"
     "    /** Height-aware consensus parameters */")

print("Block subsidy")
edit_re("src/dogecoin.cpp",
     r"CAmount GetDogecoinBlockSubsidy\(int nHeight, const Consensus::Params& consensusParams, uint256 prevHash\)\n\{.*?\n\}\n",
     """CAmount GetDogecoinBlockSubsidy(int nHeight, const Consensus::Params& consensusParams, uint256 prevHash)
{
    // 4547: 0.0495 per block, halving every nSubsidyHalvingInterval (45,470) blocks.
    const CAmount nBaseReward = 4950000; // 0.04950000
    int halvings = nHeight / consensusParams.nSubsidyHalvingInterval;
    if (halvings >= 63)
        return 0;
    CAmount nSubsidy = nBaseReward >> halvings;

    // Slow start: linear ramp from 0 over the first nSlowStartBlocks blocks.
    if (consensusParams.nSlowStartBlocks > 0 && nHeight < consensusParams.nSlowStartBlocks)
        nSubsidy = (nSubsidy * nHeight) / consensusParams.nSlowStartBlocks;

    // 4547 Block: every nBonusBlockInterval-th block pays nBonusBlockMultiplier x.
    if (consensusParams.nBonusBlockInterval > 0 && nHeight > 0 &&
        nHeight % consensusParams.nBonusBlockInterval == 0)
        nSubsidy *= consensusParams.nBonusBlockMultiplier;

    return nSubsidy;
}
""")

print("LWMA difficulty")
edit("src/pow.cpp",
     "unsigned int GetNextWorkRequired(const CBlockIndex* pindexLast, const CBlockHeader *pblock, const Consensus::Params& params)\n{\n    unsigned int nProofOfWorkLimit = UintToArith256(params.powLimit).GetCompact();\n\n    // Genesis block\n    if (pindexLast == NULL)\n        return nProofOfWorkLimit;\n",
     """// 4547: LWMA-1 by zawy12 (per-block linearly weighted moving average).
static unsigned int Lwma1CalculateNextWorkRequired(const CBlockIndex* pindexLast, const Consensus::Params& params)
{
    const int64_t T = params.nPowTargetSpacing;
    const int64_t N = params.nLwmaWindow;
    const int64_t k = N * (N + 1) * T / 2;
    const int64_t height = pindexLast->nHeight;
    const arith_uint256 powLimit = UintToArith256(params.powLimit);

    if (height < N)
        return powLimit.GetCompact();

    arith_uint256 avgTarget, nextTarget;
    int64_t thisTimestamp, previousTimestamp;
    int64_t t = 0, j = 0;

    const CBlockIndex* blockPreviousTimestamp = pindexLast->GetAncestor(height - N);
    previousTimestamp = blockPreviousTimestamp->GetBlockTime();

    for (int64_t i = height - N + 1; i <= height; i++) {
        const CBlockIndex* block = pindexLast->GetAncestor(i);
        thisTimestamp = (block->GetBlockTime() > previousTimestamp) ? block->GetBlockTime() : previousTimestamp + 1;
        int64_t solvetime = std::min(6 * T, thisTimestamp - previousTimestamp);
        previousTimestamp = thisTimestamp;
        j++;
        t += solvetime * j;
        arith_uint256 target;
        target.SetCompact(block->nBits);
        avgTarget += target / N / k;
    }
    nextTarget = t * avgTarget;
    if (nextTarget > powLimit)
        nextTarget = powLimit;
    return nextTarget.GetCompact();
}

unsigned int GetNextWorkRequired(const CBlockIndex* pindexLast, const CBlockHeader *pblock, const Consensus::Params& params)
{
    unsigned int nProofOfWorkLimit = UintToArith256(params.powLimit).GetCompact();

    // Genesis block
    if (pindexLast == NULL)
        return nProofOfWorkLimit;

    // 4547: LWMA when enabled for this network
    if (params.nLwmaWindow > 0) {
        if (params.fPowNoRetargeting)
            return pindexLast->nBits;
        return Lwma1CalculateNextWorkRequired(pindexLast, params);
    }
""")

print("Future time limit (LWMA needs a tight FTL)")
edit("src/validation.cpp",
     "    if (block.GetBlockTime() > nAdjustedTime + 2 * 60 * 60)",
     "    if (block.GetBlockTime() > nAdjustedTime + 1350) // 4547: FTL = N*T/20 for LWMA-45")
edit("src/init.cpp",
     "if (tip && tip->nTime > GetAdjustedTime() + 2 * 60 * 60) {",
     "if (tip && tip->nTime > GetAdjustedTime() + 1350) {")
edit("src/timedata.h",
     "static const int64_t DEFAULT_MAX_TIME_ADJUSTMENT = 70 * 60;",
     "static const int64_t DEFAULT_MAX_TIME_ADJUSTMENT = 10 * 60; // 4547: must stay below FTL/2")

print("Fees scaled for a 4,547-coin supply")
edit("src/policy/policy.h",
     "static const CAmount RECOMMENDED_MIN_TX_FEE = COIN / 100;",
     "static const CAmount RECOMMENDED_MIN_TX_FEE = 10000; // 4547: 0.0001 per kB (min relay 0.00001/kB, dust 0.0001)")
edit("src/wallet/wallet.h",
     "static const CAmount DEFAULT_DISCARD_THRESHOLD = COIN / 100;",
     "static const CAmount DEFAULT_DISCARD_THRESHOLD = RECOMMENDED_MIN_TX_FEE;")
edit("src/policy/fees.h",
     "static constexpr double MIN_FEERATE = COIN / 1000.0;",
     "static constexpr double MIN_FEERATE = 1000.0;")
edit("src/policy/fees.h",
     "static const double MAX_FEERATE = COIN * 10.0;",
     "static const double MAX_FEERATE = COIN / 10.0;")
edit("src/dogecoin-fees.cpp",
     "return CFeeRate(COIN / 100 * 521); // 5.21 DOGE, but very carefully avoiding floating point maths",
     "return CFeeRate(CWallet::minTxFee.GetFeePerK() * 1000);")

print("Data dir, conf file, RPC port")
edit("src/util.cpp", 'const char * const BITCOIN_CONF_FILENAME = "dogecoin.conf";',
                     'const char * const BITCOIN_CONF_FILENAME = "4547.conf";')
edit("src/util.cpp", 'return GetSpecialFolderPath(CSIDL_APPDATA) / "Dogecoin";',
                     'return GetSpecialFolderPath(CSIDL_APPDATA) / "4547";')
edit("src/util.cpp", 'return pathRet / "Library/Application Support/Dogecoin";',
                     'return pathRet / "Library/Application Support/4547";')
edit("src/util.cpp", 'return pathRet / ".dogecoin";', 'return pathRet / ".4547";')
edit("src/chainparamsbase.cpp", "        nRPCPort = 22555;", "        nRPCPort = 4545;")

print("Boost 1.83 build fix (Ubuntu 24.04)")
edit("src/init.cpp", "uiInterface.NotifyBlockTip.connect(BlockNotifyGenesisWait);", "uiInterface.NotifyBlockTip.connect(&BlockNotifyGenesisWait);")
edit("src/init.cpp", "uiInterface.NotifyBlockTip.disconnect(BlockNotifyGenesisWait);", "uiInterface.NotifyBlockTip.disconnect(&BlockNotifyGenesisWait);")

print("Mainnet chain parameters")
MAIN = f'''class CMainParams : public CChainParams {{
private:
    Consensus::Params auxpowConsensus;
public:
    CMainParams() {{
        strNetworkID = "main";

        // ---- 4547 emission ----
        consensus.nSubsidyHalvingInterval = 45470;   // ~316 days
        consensus.nSlowStartBlocks = 450;            // ~3 day reward ramp at launch
        consensus.nBonusBlockInterval = 4547;        // the 4547 Block
        consensus.nBonusBlockMultiplier = 47;        // pays 47x
        consensus.fSimplifiedRewards = true;

        // ---- difficulty ----
        consensus.powLimit = uint256S("0x00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
        consensus.nPowTargetSpacing = 10 * 60;       // 10 minute blocks
        consensus.nPowTargetTimespan = 10 * 60;
        consensus.nLwmaWindow = 45;                  // LWMA-45
        consensus.fDigishieldDifficultyCalculation = false;
        consensus.fPowAllowMinDifficultyBlocks = false;
        consensus.fPowAllowDigishieldMinDifficultyBlocks = false;
        consensus.fPowNoRetargeting = false;

        consensus.nCoinbaseMaturity = 47;

        // All soft forks active from the start
        consensus.nMajorityEnforceBlockUpgrade = 1500;
        consensus.nMajorityRejectBlockOutdated = 1900;
        consensus.nMajorityWindow = 2000;
        consensus.BIP34Height = 1;
        consensus.BIP34Hash = uint256();
        consensus.BIP65Height = 1;
        consensus.BIP66Height = 1;
        consensus.nRuleChangeActivationThreshold = 4320; // 95% of 4547
        consensus.nMinerConfirmationWindow = 4547;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].bit = 28;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].nStartTime = 1199145601;
        consensus.vDeployments[Consensus::DEPLOYMENT_TESTDUMMY].nTimeout = 1230767999;
        consensus.vDeployments[Consensus::DEPLOYMENT_CSV].bit = 0;
        consensus.vDeployments[Consensus::DEPLOYMENT_CSV].nStartTime = 1462060800;
        consensus.vDeployments[Consensus::DEPLOYMENT_CSV].nTimeout = 1493596800;
        consensus.vDeployments[Consensus::DEPLOYMENT_SEGWIT].bit = 1;
        consensus.vDeployments[Consensus::DEPLOYMENT_SEGWIT].nStartTime = 1479168000;
        consensus.vDeployments[Consensus::DEPLOYMENT_SEGWIT].nTimeout = 0;

        consensus.nMinimumChainWork = uint256S("0x00");
        consensus.defaultAssumeValid = uint256S("0x00");

        // ---- AuxPoW (merge mining) ----
        // Blocks 0-4546: normal Scrypt mining only, AuxPoW blocks rejected.
        // Block 4547+:   AuxPoW (merge mining) allowed alongside normal mining.
        consensus.nAuxpowChainId = 0x11C3;           // 4547
        consensus.fStrictChainId = true;
        consensus.fAllowLegacyBlocks = true;         // true = AuxPoW NOT yet active
        consensus.nHeightEffective = 0;

        auxpowConsensus = consensus;
        auxpowConsensus.nHeightEffective = 4547;
        auxpowConsensus.fAllowLegacyBlocks = false;  // false = AuxPoW active
        auxpowConsensus.pLeft = nullptr;
        auxpowConsensus.pRight = nullptr;

        consensus.pRight = &auxpowConsensus;
        pConsensusRoot = &consensus;

        // ---- network ----
        pchMessageStart[0] = 0x45;
        pchMessageStart[1] = 0x47;
        pchMessageStart[2] = 0x45;
        pchMessageStart[3] = 0x47;
        nDefaultPort = 4547;
        nPruneAfterHeight = 100000;

        const char* pszTimestamp = "{GENESIS_MSG}";
        const CScript genesisOutputScript = CScript() << OP_RETURN;
        genesis = CreateGenesisBlock(pszTimestamp, genesisOutputScript, {GENESIS_TIME}, {GENESIS_NONCE}, 0x1e0ffff0, 1, 0);
        consensus.hashGenesisBlock = genesis.GetHash();
        auxpowConsensus.hashGenesisBlock = consensus.hashGenesisBlock;
        assert(consensus.hashGenesisBlock == uint256S("{GENESIS_HASH}"));
        assert(genesis.hashMerkleRoot == uint256S("{GENESIS_MERKLE}"));

        vSeeds.clear();
        vFixedSeeds.clear();

        base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,8);    // addresses start with 4
        base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,15);   // script addresses start with 7
        base58Prefixes[SECRET_KEY] =     std::vector<unsigned char>(1,136);
        base58Prefixes[EXT_PUBLIC_KEY] = boost::assign::list_of(0x04)(0x88)(0xB2)(0x1E).convert_to_container<std::vector<unsigned char> >();
        base58Prefixes[EXT_SECRET_KEY] = boost::assign::list_of(0x04)(0x88)(0xAD)(0xE4).convert_to_container<std::vector<unsigned char> >();

        fMiningRequiresPeers = false;   // lets a single launch node serve the pool; set true once the network has peers
        fDefaultConsistencyChecks = false;
        fRequireStandard = true;
        fMineBlocksOnDemand = false;

        checkpointData = (CCheckpointData) {{
            boost::assign::map_list_of
            ( 0, uint256S("{GENESIS_HASH}"))
        }};

        chainTxData = ChainTxData{{ {GENESIS_TIME}, 0, 0 }};
    }}
}};
static CMainParams mainParams;
'''
edit_re("src/chainparams.cpp", r"class CMainParams : public CChainParams \{.*?\nstatic CMainParams mainParams;\n", MAIN)
print("\nDone. 4547 consensus changes applied.")
