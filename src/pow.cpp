// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2016 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include "pow.h"

#include "auxpow.h"
#include "arith_uint256.h"
#include "chain.h"
#include "dogecoin.h"
#include "primitives/block.h"
#include "uint256.h"
#include "util.h"

// Determine if the for the given block, a min difficulty setting applies
bool AllowMinDifficultyForBlock(const CBlockIndex* pindexLast, const CBlockHeader *pblock, const Consensus::Params& params)
{
    // check if the chain allows minimum difficulty blocks
    if (!params.fPowAllowMinDifficultyBlocks)
        return false;

    // Dogecoin: Magic number at which reset protocol switches
    // check if we allow minimum difficulty at this block-height
    if (pindexLast->nHeight < 157500)
        return false;

    // Allow for a minimum block time if the elapsed time > 2*nTargetSpacing
    return (pblock->GetBlockTime() > pindexLast->GetBlockTime() + params.nPowTargetSpacing*2);
}

// 4547: LWMA-1 by zawy12 (per-block linearly weighted moving average).
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

    // Dogecoin: Special rules for minimum difficulty blocks with Digishield
    if (AllowDigishieldMinDifficultyForBlock(pindexLast, pblock, params))
    {
        // Special difficulty rule for testnet:
        // If the new block's timestamp is more than 2* nTargetSpacing minutes
        // then allow mining of a min-difficulty block.
        return nProofOfWorkLimit;
    }

    // Only change once per difficulty adjustment interval
    bool fNewDifficultyProtocol = (pindexLast->nHeight >= 145000);
    const int64_t difficultyAdjustmentInterval = fNewDifficultyProtocol
                                                 ? 1
                                                 : params.DifficultyAdjustmentInterval();
    if ((pindexLast->nHeight+1) % difficultyAdjustmentInterval != 0)
    {
        if (params.fPowAllowMinDifficultyBlocks)
        {
            // Special difficulty rule for testnet:
            // If the new block's timestamp is more than 2* 10 minutes
            // then allow mining of a min-difficulty block.
            if (pblock->GetBlockTime() > pindexLast->GetBlockTime() + params.nPowTargetSpacing*2)
                return nProofOfWorkLimit;
            else
            {
                // Return the last non-special-min-difficulty-rules-block
                const CBlockIndex* pindex = pindexLast;
                while (pindex->pprev && pindex->nHeight % params.DifficultyAdjustmentInterval() != 0 && pindex->nBits == nProofOfWorkLimit)
                    pindex = pindex->pprev;
                return pindex->nBits;
            }
        }
        return pindexLast->nBits;
    }

    // Litecoin: This fixes an issue where a 51% attack can change difficulty at will.
    // Go back the full period unless it's the first retarget after genesis. Code courtesy of Art Forz
    int blockstogoback = difficultyAdjustmentInterval-1;
    if ((pindexLast->nHeight+1) != difficultyAdjustmentInterval)
        blockstogoback = difficultyAdjustmentInterval;

    // Go back by what we want to be 14 days worth of blocks
    int nHeightFirst = pindexLast->nHeight - blockstogoback;
    assert(nHeightFirst >= 0);
    const CBlockIndex* pindexFirst = pindexLast->GetAncestor(nHeightFirst);
    assert(pindexFirst);

    return CalculateDogecoinNextWorkRequired(pindexLast, pindexFirst->GetBlockTime(), params);
}

unsigned int CalculateNextWorkRequired(const CBlockIndex* pindexLast, int64_t nFirstBlockTime, const Consensus::Params& params)
{
    if (params.fPowNoRetargeting)
        return pindexLast->nBits;

    // Limit adjustment step
    int64_t nActualTimespan = pindexLast->GetBlockTime() - nFirstBlockTime;
    if (nActualTimespan < params.nPowTargetTimespan/4)
        nActualTimespan = params.nPowTargetTimespan/4;
    if (nActualTimespan > params.nPowTargetTimespan*4)
        nActualTimespan = params.nPowTargetTimespan*4;

    // Retarget
    const arith_uint256 bnPowLimit = UintToArith256(params.powLimit);
    arith_uint256 bnNew;
    bnNew.SetCompact(pindexLast->nBits);
    bnNew *= nActualTimespan;
    bnNew /= params.nPowTargetTimespan;

    if (bnNew > bnPowLimit)
        bnNew = bnPowLimit;

    return bnNew.GetCompact();
}

bool CheckProofOfWork(uint256 hash, unsigned int nBits, const Consensus::Params& params)
{
    bool fNegative;
    bool fOverflow;
    arith_uint256 bnTarget;

    bnTarget.SetCompact(nBits, &fNegative, &fOverflow);

    // Check range
    if (fNegative || bnTarget == 0 || fOverflow || bnTarget > UintToArith256(params.powLimit))
        return false;

    // Check proof of work matches claimed amount
    if (UintToArith256(hash) > bnTarget)
        return false;

    return true;
}
