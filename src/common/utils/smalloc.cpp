//
// Created by kingdo on 23-3-13.
//

#include <df/utils/smalloc.h>
#include <df/utils/log.h>

namespace df::utils {

    StaticAllocatableMemory::StaticAllocatableMemory(void *addr, size_t len, bool init) :
            start_addr(addr), length(len), initSector(nullptr), nextFreeSector(nullptr) {
        DF_CHECK_WITH_EXIT(addr != nullptr, "StaticAllocatableMemory Init error, start_addr is NULL.");
        DF_CHECK_WITH_EXIT(len >= PAGE_SIZE && len % PAGE_SIZE == 0, "Length must be a multiple of pages.");

        if (init) {
            SPDLOG_DEBUG("Initializing the StaticAllocatableMemory for the 1st time");
            memset(addr, 0, len);

            SPDLOG_DEBUG("Initialize the first sector of the StaticAllocatableMemory");
            initSector = makeNewSector(addr, len - SIZE_OF_SECTOR, nullptr);
            nextFreeSector = initSector;
        } else {
            initSector = static_cast<sector *>(addr);
            DF_CHECK_WITH_EXIT(isValidSector(initSector), "Load Failed: First Sector is invalid");
            uint64_t size_test = 0;
            for (auto *currentSector = initSector;
                 isValidSector(currentSector);
                 currentSector = getRightSector(currentSector)) {
                if (currentSector->isFree)
                    nextFreeSector = currentSector;
                size_test += (SIZE_OF_SECTOR + currentSector->size);
            }
            if (nextFreeSector == nullptr) {
                SPDLOG_WARN("There is no free space");
            }
            DF_CHECK_WITH_EXIT(size_test == length, "Load Failed: Size Check un-success");
        }
    }

    void *StaticAllocatableMemory::malloc(size_t size) {
        SPDLOG_DEBUG("malloc {} bytes", size);

        UniqueLock lock(staticAllocatableMemoryMutex);

        // Jump from sector to sector untill you find a free sector with enough space
        auto *currentSector = nextFreeSector;
        while (currentSector != nullptr) {
            // Check if the current sector is good for use
            if (currentSector->isFree && currentSector->size >= size) {
                // Check if, after allocating the memory, will there be enough space for another sector
                if (currentSector->size - size > SIZE_OF_SECTOR) {
                    auto *newSector = makeNewSector((char *) currentSector + SIZE_OF_SECTOR + size,
                                                    currentSector->size - SIZE_OF_SECTOR - size,
                                                    currentSector);
                    auto *currentRightSector = this->getRightSector(currentSector);
                    if (currentRightSector != nullptr)
                        currentRightSector->prevSector = newSector;
                }
                    // if not use the whole size which may be greater than the size requested
                else {
                    SPDLOG_WARN("Allocating a size of {} instead of {}. Reason: BufferWaste",
                                currentSector->size, size);
                    size = currentSector->size;
                }
                // Update the current sector
                currentSector->size = size;
                currentSector->isFree = false;
                auto rightS = getRightSector(currentSector);
                nextFreeSector = rightS == nullptr ? rightS : initSector;
                return (void *) ((char *) currentSector + SIZE_OF_SECTOR);
            }
            currentSector = getRightSector(currentSector);
            SPDLOG_DEBUG("Moving next Sector, addr: {:p}", (void *) currentSector);
        }
        SPDLOG_ERROR("Sector out of range: {:p}", (void *) currentSector);
        return nullptr;
    }

    void StaticAllocatableMemory::free(void *pAddress) {
        SPDLOG_DEBUG("free {}", pAddress);

        UniqueLock lock(staticAllocatableMemoryMutex);

        auto *pSector = getSectorFromAddress(pAddress);
        DF_CHECK_WITH_EXIT(pSector != nullptr,
                           fmt::format("Provided Address at %p does not point to a valid sector", pAddress));
        pSector->isFree = true;
        memset((char *) pSector + SIZE_OF_SECTOR, 0, pSector->size);

        // Merge with surrounding sectors if possible
        auto *pLestSector = getLeftSector(pSector);
        auto *pRightSector = getRightSector(pSector);

        if (pRightSector != nullptr) {
            if (pRightSector->isFree) {
                SPDLOG_DEBUG("Merging with the Right Sector");
                auto *pRightRightSector = getRightSector(pRightSector);
                if (isValidSector(pRightRightSector)) {
                    pRightRightSector->prevSector = pSector;
                }

                pSector->size += pRightSector->size + SIZE_OF_SECTOR;

                memset((char *) pRightSector, 0, SIZE_OF_SECTOR);

                // update pRightSector for merge with left
                pRightSector = getRightSector(pSector);
            }
        } else {
            SPDLOG_DEBUG("There is no sector on the right");
        }

        if (pLestSector != nullptr) {
            if (pLestSector->isFree) {
                SPDLOG_DEBUG("Merging with the Left sector");
                pLestSector->size += pSector->size + SIZE_OF_SECTOR;
                memset((char *) pSector, 0, SIZE_OF_SECTOR);
                if (pRightSector != nullptr)
                    pRightSector->prevSector = pLestSector;
            }
        } else {
            SPDLOG_DEBUG("There is no sector on the left");
        }
    }

    bool StaticAllocatableMemory::isValidSector(sector *pstSector) {

        if ((void *) pstSector < start_addr ||
            (uint64_t) pstSector >= (uint64_t) start_addr + length - SIZE_OF_SECTOR ||
            strcmp(pstSector->sector_magic, StaticAllocatableMemorySectorMagic) != 0) {
            return false;
        }
        return true;
    }

    StaticAllocatableMemory::sector *
    StaticAllocatableMemory::makeNewSector(void *addr, size_t size, StaticAllocatableMemory::sector *prevSector) {
        if (prevSector != nullptr)
            DF_CHECK_WITH_EXIT(isValidSector(prevSector), "prevSector is not Valid!");
        DF_CHECK_WITH_EXIT(size > 0 && size <= length - SIZE_OF_SECTOR, "size is not Valid!");
        DF_CHECK_WITH_EXIT(addr >= start_addr &&
                           (uint64_t) addr < uint64_t(start_addr) + length - SIZE_OF_SECTOR,
                           "Addr is not Valid to create Sector");
        auto *newSector = (sector *) addr;
        newSector->isFree = true;
        strcpy(newSector->sector_magic, StaticAllocatableMemorySectorMagic);
        newSector->prevSector = prevSector;
        newSector->size = size;
        return newSector;
    }

    StaticAllocatableMemory::sector *StaticAllocatableMemory::getRightSector(StaticAllocatableMemory::sector *pSector) {
        DF_CHECK_WITH_EXIT(isValidSector(pSector), "Sector is not Valid!");
        auto *right = (sector *) (((char *) pSector) + SIZE_OF_SECTOR + pSector->size);
        if (!isValidSector(right))
            right = nullptr;
        return right;
    }

    StaticAllocatableMemory::sector *StaticAllocatableMemory::getLeftSector(StaticAllocatableMemory::sector *pSector) {
        DF_CHECK_WITH_EXIT(isValidSector(pSector), "Sector is not Valid!");
        auto *left = pSector->prevSector;
        if (left == nullptr)
            DF_CHECK_WITH_EXIT(pSector == (sector *) start_addr, "Error, Sector is not initSector");
        return pSector->prevSector;
    }

    StaticAllocatableMemory::sector *StaticAllocatableMemory::getSectorFromAddress(void *address) {
        auto *s = (sector *) ((char *) address - SIZE_OF_SECTOR);
        if (!isValidSector(s)) {
            SPDLOG_WARN("Sector is not Valid, from address {:p}", address);
            s = nullptr;
        }
        return s;
    }

    uint64_t StaticAllocatableMemory::address2offset(void *address) {
        return (uint64_t) address - (uint64_t) start_addr;
    }

    void *StaticAllocatableMemory::offset2address(uint64_t offset) {
        return (char *) start_addr + offset;
    }

    void StaticAllocatableMemory::traverseData(const std::function<void(char *)> &func) {
        for (auto *currentSector = initSector;
             isValidSector(currentSector);
             currentSector = getRightSector(currentSector)) {
            if (currentSector->isFree)
                continue;
            func((char *) currentSector + SIZE_OF_SECTOR);
        }
    }
}