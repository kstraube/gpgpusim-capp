#!/bin/bash
. /root/env
cd /home/kkstraube/gpgpu-sim
source setup_environment
cd pannotia/color/run_color_max
./color_max ../../dataset/color/G3_circuit.graph 1> output