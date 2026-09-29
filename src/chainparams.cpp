// Copyright (c) 2010 Satoshi Nakamoto
// Copyright (c) 2009-2016 The Bitcoin Core developers
// Copyright (c) 2022-2024 The Dogecoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include "chainparams.h"
#include "consensus/merkle.h"

#include "tinyformat.h"
#include "util.h"
#include "utilstrencodings.h"

#include <assert.h>

#include <boost/assign/list_of.hpp>

#include "chainparamsseeds.h"

static CBlock CreateGenesisBlock(const char* pszTimestamp, const CScript& genesisOutputScript, uint32_t nTime, uint32_t nNonce, uint32_t nBits, int32_t nVersion, const CAmount& genesisReward)
{
    CMutableTransaction txNew;
    txNew.nVersion = 1;
    txNew.vin.resize(1);
    txNew.vout.resize(1);
    txNew.vin[0].scriptSig = CScript() << 486604799 << CScriptNum(4) << std::vector<unsigned char>((const unsigned char*)pszTimestamp, (const unsigned char*)pszTimestamp + strlen(pszTimestamp));
    txNew.vout[0].nValue = genesisReward;
    txNew.vout[0].scriptPubKey = genesisOutputScript;

    CBlock genesis;
    genesis.nTime    = nTime;
    genesis.nBits    = nBits;
    genesis.nNonce   = nNonce;
    genesis.nVersion = nVersion;
    genesis.vtx.push_back(MakeTransactionRef(std::move(txNew)));
    genesis.hashPrevBlock.SetNull();
    genesis.hashMerkleRoot = BlockMerkleRoot(genesis);
    return genesis;
}

/**
 * Build the genesis block. Note that the output of its generation
 * transaction cannot be spent since it did not originally exist in the
 * database.
 *
 * CBlock(hash=000000000019d6, ver=1, hashPrevBlock=00000000000000, hashMerkleRoot=4a5e1e, nTime=1386325540, nBits=0x1e0ffff0, nNonce=99943, vtx=1)
 *   CTransaction(hash=4a5e1e, ver=1, vin.size=1, vout.size=1, nLockTime=0)
 *     CTxIn(COutPoint(000000, -1), coinbase 04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73)
 *     CTxOut(nValue=50.00000000, scriptPubKey=0x5F1DF16B2B704C8A578D0B)
 *   vMerkleTree: 4a5e1e
 */
static CBlock CreateGenesisBlock(uint32_t nTime, uint32_t nNonce, uint32_t nBits, int32_t nVersion, const CAmount& genesisReward)
{
    const char* pszTimestamp = "Nintondo";
    const CScript genesisOutputScript = CScript() << ParseHex("040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9") << OP_CHECKSIG;
    return CreateGenesisBlock(pszTimestamp, genesisOutputScript, nTime, nNonce, nBits, nVersion, genesisReward);
}

/**
 * Main network
 */
/**
 * What makes a good checkpoint block?
 * + Is surrounded by blocks with reasonable timestamps
 *   (no blocks before with a timestamp after, none after with
 *    timestamp before)
 * + Contains no strange transactions
 */

class CMainParams : public CChainParams {
private:
    Consensus::Params auxpowConsensus;
public:
    CMainParams() {
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

        const char* pszTimestamp = "45 came first. 47 came back. 4547 begins.";
        const CScript genesisOutputScript = CScript() << OP_RETURN;
        genesis = CreateGenesisBlock(pszTimestamp, genesisOutputScript, 1793103750, 88204, 0x1e0ffff0, 1, 0);
        consensus.hashGenesisBlock = genesis.GetHash();
        auxpowConsensus.hashGenesisBlock = consensus.hashGenesisBlock;
        assert(consensus.hashGenesisBlock == uint256S("0x400cef90ca67f6a0f85d14d2ec3b1ade5acff17f02043c02f9733c413ee3a273"));
        assert(genesis.hashMerkleRoot == uint256S("0xf052a2c5a763af37e569623b9a20b04f43b6f6bc1cc07bbdb5c8ccb4911d2632"));

        vSeeds.clear();
        vFixedSeeds.clear();
        vSeeds.push_back(CDNSSeedData("seed1.4547coin.net", "seed1.4547coin.net"));
        vSeeds.push_back(CDNSSeedData("seed2.4547coin.net", "seed2.4547coin.net"));

        base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,8);    // addresses start with 4
        base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,15);   // script addresses start with 7
        base58Prefixes[SECRET_KEY] =     std::vector<unsigned char>(1,136);
        base58Prefixes[EXT_PUBLIC_KEY] = boost::assign::list_of(0x04)(0x88)(0xB2)(0x1E).convert_to_container<std::vector<unsigned char> >();
        base58Prefixes[EXT_SECRET_KEY] = boost::assign::list_of(0x04)(0x88)(0xAD)(0xE4).convert_to_container<std::vector<unsigned char> >();

        fMiningRequiresPeers = false;   // lets a single launch node serve the pool; set true once the network has peers
        fDefaultConsistencyChecks = false;
        fRequireStandard = true;
        fMineBlocksOnDemand = false;

        checkpointData = (CCheckpointData) {
            boost::assign::map_list_of
            ( 0, uint256S("0x400cef90ca67f6a0f85d14d2ec3b1ade5acff17f02043c02f9733c413ee3a273"))
        };

        chainTxData = ChainTxData{ 1793103750, 0, 0 };
    }
};
static CMainParams mainParams;

/**
 * Testnet (v3)
 */
class CTestNetParams : public CChainParams {
private:
    Consensus::Params auxpowConsensus;
public:
    CTestNetParams() {
        strNetworkID = "test";

        // Same 4547 emission rules as mainnet
        consensus.nSubsidyHalvingInterval = 45470;
        consensus.nSlowStartBlocks = 450;
        consensus.nBonusBlockInterval = 4547;
        consensus.nBonusBlockMultiplier = 47;
        consensus.fSimplifiedRewards = true;

        consensus.powLimit = uint256S("0x000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
        consensus.nPowTargetSpacing = 10 * 60;
        consensus.nPowTargetTimespan = 10 * 60;
        consensus.nLwmaWindow = 45;
        consensus.fDigishieldDifficultyCalculation = false;
        consensus.fPowAllowMinDifficultyBlocks = false;
        consensus.fPowAllowDigishieldMinDifficultyBlocks = false;
        consensus.fPowNoRetargeting = false;
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

        // AuxPoW (merge mining) switches on at block 45 on this network
        consensus.nAuxpowChainId = 0x11C3;
        consensus.fStrictChainId = true;
        consensus.fAllowLegacyBlocks = true;
        consensus.nHeightEffective = 0;
        auxpowConsensus = consensus;
        auxpowConsensus.nHeightEffective = 45;
        auxpowConsensus.fAllowLegacyBlocks = false;
        auxpowConsensus.pLeft = nullptr;
        auxpowConsensus.pRight = nullptr;
        consensus.pRight = &auxpowConsensus;
        pConsensusRoot = &consensus;

        pchMessageStart[0] = 0x34;
        pchMessageStart[1] = 0x35;
        pchMessageStart[2] = 0x34;
        pchMessageStart[3] = 0x37;
        nDefaultPort = 14547;
        nPruneAfterHeight = 1000;

        const char* pszTimestamp = "4547 testnet - 45 came first. 47 came back.";
        const CScript genesisOutputScript = CScript() << OP_RETURN;
        genesis = CreateGenesisBlock(pszTimestamp, genesisOutputScript, 1790208000, 3637, 0x1f0fffff, 1, 0);
        consensus.hashGenesisBlock = genesis.GetHash();
        auxpowConsensus.hashGenesisBlock = consensus.hashGenesisBlock;
        assert(consensus.hashGenesisBlock == uint256S("0x66f73c8787a7907858fbfa28266c8077f588f564f249301a8b72ee150e0450e2"));
        assert(genesis.hashMerkleRoot == uint256S("0x8078a5ba8cc40c8396568a8fabf69f2c34aa00d5ed6f3a53a59f4c4dda7a796e"));

        vSeeds.clear();
        vFixedSeeds.clear();
        vSeeds.push_back(CDNSSeedData("testseed1.4547coin.net", "testseed1.4547coin.net"));

        base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,127);
        base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,196);
        base58Prefixes[SECRET_KEY] =     std::vector<unsigned char>(1,239);
        base58Prefixes[EXT_PUBLIC_KEY] = boost::assign::list_of(0x04)(0x35)(0x87)(0xCF).convert_to_container<std::vector<unsigned char> >();
        base58Prefixes[EXT_SECRET_KEY] = boost::assign::list_of(0x04)(0x35)(0x83)(0x94).convert_to_container<std::vector<unsigned char> >();

        fMiningRequiresPeers = false;
        fDefaultConsistencyChecks = false;
        fRequireStandard = false;
        fMineBlocksOnDemand = false;

        checkpointData = (CCheckpointData) {
            boost::assign::map_list_of
            ( 0, uint256S("0x66f73c8787a7907858fbfa28266c8077f588f564f249301a8b72ee150e0450e2"))
        };
        chainTxData = ChainTxData{ 1790208000, 0, 0 };
    }

    void UpdateBIP9Parameters(Consensus::DeploymentPos d, int64_t nStartTime, int64_t nTimeout)
    {
        consensus.vDeployments[d].nStartTime = nStartTime;
        consensus.vDeployments[d].nTimeout = nTimeout;
    }
};
static CTestNetParams testNetParams;

/**
 * Regression test
 */
class CRegTestParams : public CChainParams {
private:
    Consensus::Params auxpowConsensus;
public:
    CRegTestParams() {
        strNetworkID = "regtest";

        // Same 4547 emission rules as mainnet
        consensus.nSubsidyHalvingInterval = 45470;
        consensus.nSlowStartBlocks = 450;
        consensus.nBonusBlockInterval = 4547;
        consensus.nBonusBlockMultiplier = 47;
        consensus.fSimplifiedRewards = true;

        consensus.powLimit = uint256S("0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
        consensus.nPowTargetSpacing = 10 * 60;
        consensus.nPowTargetTimespan = 10 * 60;
        consensus.nLwmaWindow = 45;
        consensus.fDigishieldDifficultyCalculation = false;
        consensus.fPowAllowMinDifficultyBlocks = false;
        consensus.fPowAllowDigishieldMinDifficultyBlocks = false;
        consensus.fPowNoRetargeting = true;
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

        // AuxPoW (merge mining) switches on at block 45 on this network
        consensus.nAuxpowChainId = 0x11C3;
        consensus.fStrictChainId = true;
        consensus.fAllowLegacyBlocks = true;
        consensus.nHeightEffective = 0;
        auxpowConsensus = consensus;
        auxpowConsensus.nHeightEffective = 45;
        auxpowConsensus.fAllowLegacyBlocks = false;
        auxpowConsensus.pLeft = nullptr;
        auxpowConsensus.pRight = nullptr;
        consensus.pRight = &auxpowConsensus;
        pConsensusRoot = &consensus;

        pchMessageStart[0] = 0x52;
        pchMessageStart[1] = 0x34;
        pchMessageStart[2] = 0x35;
        pchMessageStart[3] = 0x37;
        nDefaultPort = 18547;
        nPruneAfterHeight = 1000;

        const char* pszTimestamp = "4547 regtest";
        const CScript genesisOutputScript = CScript() << OP_RETURN;
        genesis = CreateGenesisBlock(pszTimestamp, genesisOutputScript, 1790208000, 2, 0x207fffff, 1, 0);
        consensus.hashGenesisBlock = genesis.GetHash();
        auxpowConsensus.hashGenesisBlock = consensus.hashGenesisBlock;
        assert(consensus.hashGenesisBlock == uint256S("0xb256b7027f4aff043deb4554c26e759f61cf8e21c4414ee055d3efa7f8cff59f"));
        assert(genesis.hashMerkleRoot == uint256S("0x494ab230aa3ff8ce684b2520141ac45e1c501d6174b1e1acf9574ba2122a5c07"));

        vSeeds.clear();
        vFixedSeeds.clear();

        base58Prefixes[PUBKEY_ADDRESS] = std::vector<unsigned char>(1,122);
        base58Prefixes[SCRIPT_ADDRESS] = std::vector<unsigned char>(1,196);
        base58Prefixes[SECRET_KEY] =     std::vector<unsigned char>(1,239);
        base58Prefixes[EXT_PUBLIC_KEY] = boost::assign::list_of(0x04)(0x35)(0x87)(0xCF).convert_to_container<std::vector<unsigned char> >();
        base58Prefixes[EXT_SECRET_KEY] = boost::assign::list_of(0x04)(0x35)(0x83)(0x94).convert_to_container<std::vector<unsigned char> >();

        fMiningRequiresPeers = false;
        fDefaultConsistencyChecks = true;
        fRequireStandard = false;
        fMineBlocksOnDemand = true;

        checkpointData = (CCheckpointData) {
            boost::assign::map_list_of
            ( 0, uint256S("0xb256b7027f4aff043deb4554c26e759f61cf8e21c4414ee055d3efa7f8cff59f"))
        };
        chainTxData = ChainTxData{ 1790208000, 0, 0 };
    }

    void UpdateBIP9Parameters(Consensus::DeploymentPos d, int64_t nStartTime, int64_t nTimeout)
    {
        consensus.vDeployments[d].nStartTime = nStartTime;
        consensus.vDeployments[d].nTimeout = nTimeout;
    }
};
static CRegTestParams regTestParams;

static CChainParams *pCurrentParams = 0;

const CChainParams &Params() {
    assert(pCurrentParams);
    return *pCurrentParams;
}

const Consensus::Params *Consensus::Params::GetConsensus(uint32_t nTargetHeight) const {
    if (nTargetHeight < this -> nHeightEffective && this -> pLeft != NULL) {
        return this -> pLeft -> GetConsensus(nTargetHeight);
    } else if (nTargetHeight > this -> nHeightEffective && this -> pRight != NULL) {
        const Consensus::Params *pCandidate = this -> pRight -> GetConsensus(nTargetHeight);
        if (pCandidate->nHeightEffective <= nTargetHeight) {
            return pCandidate;
        }
    }

    // No better match below the target height
    return this;
}

CChainParams& Params(const std::string& chain)
{
    if (chain == CBaseChainParams::MAIN)
            return mainParams;
    else if (chain == CBaseChainParams::TESTNET)
            return testNetParams;
    else if (chain == CBaseChainParams::REGTEST)
            return regTestParams;
    else
        throw std::runtime_error(strprintf("%s: Unknown chain %s.", __func__, chain));
}

void SelectParams(const std::string& network)
{
    SelectBaseParams(network);
    pCurrentParams = &Params(network);
}

void UpdateRegtestBIP9Parameters(Consensus::DeploymentPos d, int64_t nStartTime, int64_t nTimeout)
{
    regTestParams.UpdateBIP9Parameters(d, nStartTime, nTimeout);
}
