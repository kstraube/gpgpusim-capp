
FROM ubuntu:12.04

MAINTAINER Jason Lowe-Power <jason@lowepower.com>

RUN apt-get update -y && apt-get install -y \
        build-essential \
	xutils-dev \
	bison \
	zlib1g-dev \
	flex \
	libglu1-mesa-dev \
	wget

RUN wget http://developer.download.nvidia.com/compute/cuda/3_2_prod/toolkit/cudatoolkit_3.2.16_linux_64_ubuntu10.04.run
RUN wget http://developer.download.nvidia.com/compute/cuda/3_2_prod/sdk/gpucomputingsdk_3.2.16_linux.run

# Note: May need to make sure return is pressed
RUN bash cudatoolkit_3.2.16_linux_64_ubuntu10.04.run
# Note: must input /usr/local/cuda, then return
RUN bash gpucomputingsdk_3.2.16_linux.run
RUN mv /root/NVIDIA_GPU_Computing_SDK/C /usr/local/cuda && \
    mv /root/NVIDIA_GPU_Computing_SDK/shared /usr/local/cuda

RUN echo " \
    export CUDAHOME=/usr/local/cuda; \
    export PATH=$PATH:/usr/local/cuda/bin; \
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/lib; \
    export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/cuda/C/lib:/usr/local/cuda/shared/lib; \
    export CUDA_INSTALL_PATH=/usr/local/cuda; \
    export NVIDIA_COMPUTE_SDK_LOCATION=/usr/local/cuda; \
    " >> /root/env

# for this to work with interactive shell
RUN echo "source /root/env" >> /root/.bashrc

WORKDIR /usr/local/cuda/C/common
RUN make 2> /dev/null
WORKDIR /usr/local/cuda/shared
RUN make 2> /dev/null

WORKDIR /
