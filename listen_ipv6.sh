#!/bin/bash
ifconfig
socat TCP6-LISTEN:8080,fork,reuseaddr TCP:0.0.0.0:7860
