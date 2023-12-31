FROM ubuntu:22.04

RUN apt-get update

# Install Python3.10
RUN apt-get install -y \
    python3.10 python3.10-dev python3-pip

# Install C++ build tools
RUN apt-get install -y  \
    g++ make cmake

# Install base tools and dependencies
RUN apt-get install -y \
    git \
    meson \
    pkg-config \
    libboost-filesystem-dev \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/thirdparty

RUN cd /app/thirdparty && \
    git clone --depth 1 -b v1.1.0 https://github.com/Tencent/rapidjson.git && \
    cd rapidjson && mkdir build && cd build && cmake -DRAPIDJSON_BUILD_DOC=false -DRAPIDJSON_BUILD_EXAMPLES=false -DRAPIDJSON_BUILD_TESTS=false .. \
    && make -j install

RUN cd /app/thirdparty && \
    git clone --depth 1 -b v1.9.2 https://github.com/gabime/spdlog.git && \
    cd spdlog && mkdir build && cd build && cmake -DSPDLOG_BUILD_ALL=false -DSPDLOG_BUILD_SHARED=false -DSPDLOG_ENABLE_PCH=false -DSPDLOG_BUILD_EXAMPLE_HO=false -DSPDLOG_BUILD_TESTS_HO=false -DSPDLOG_BUILD_BENCH=false -DSPDLOG_SANITIZE_ADDRESS=false -DSPDLOG_BUILD_WARNINGS=false .. \
    && make -j install

RUN cd /app/thirdparty && \
    git clone --depth 1 -b 8.1.1 https://github.com/fmtlib/fmt.git && \
    cd fmt && mkdir build && cd build && cmake .. && make -j install

RUN apt-get install -y \
    git \
    pkg-config \
    libboost-filesystem-dev \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN cd /app/thirdparty && \
    git clone --depth 1 https://github.com/Kingdo777/pistache && \
    cd pistache && \
    sed -i 's\sudo\\g' ./install.sh && \
    ./install.sh

COPY . /app/state-function

WORKDIR /app/state-function

RUN mv src/state-function-action/__main__.py action.py

RUN rm -rf build &&  \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j 4 && \
    cd ..

RUN pip3 install /app/state-function/src/state-function-action/ipc-py-extend/dist/ipc-1.0.0-cp310-cp310-linux_x86_64.whl  \
    /app/state-function/src/state-function-library/statefunction-py-extend/dist/statefunction-3.0.0-cp310-cp310-linux_x86_64.whl

CMD ["python3", "server.py"]