//
// Created by kingdo on 23-3-13.
//

#ifndef DATAFUNCTION_SMALLOC_H
#define DATAFUNCTION_SMALLOC_H

#include <df/utils/macro.h>
#include <df/utils/locks.h>

#include <functional>

#define StaticAllocatableMemorySectorMagic "Kingdo"
#define SIZE_OF_SECTOR sizeof(sector)
#define PAGE_SIZE 4096

namespace df::utils {

    class StaticAllocatableMemory {

    public:
        StaticAllocatableMemory(void *addr, size_t len, bool init);

        static std::shared_ptr<StaticAllocatableMemory> CreateStaticAllocatableMemory(void *addr, size_t len) {
            return std::make_shared<StaticAllocatableMemory>(addr, len, true);
        }

        static std::shared_ptr<StaticAllocatableMemory> LoadStaticAllocatableMemory(void *addr, size_t len) {
            return std::make_shared<StaticAllocatableMemory>(addr, len, false);
        }

        void *malloc(size_t size);

        void free(void *address);

        uint64_t address2offset(void *address);

        void *offset2address(uint64_t offset);

        void traverseData(const std::function<void(char *)> &func);

    private:
        struct sector {
            bool isFree;
            char sector_magic[7];
            size_t size;
            sector *prevSector;
        };

        void *start_addr;
        size_t length;
        sector *initSector;

        /// for fast search
        sector *nextFreeSector;

        std::mutex staticAllocatableMemoryMutex;

        sector *getSectorFromAddress(void *address);

        sector *getLeftSector(sector *pSector);

        sector *getRightSector(sector *pSector);

        sector *makeNewSector(void *addr, size_t size, sector *prevSector);

        bool isValidSector(sector *pSector);

    };
}


#endif //DATAFUNCTION_SMALLOC_H
