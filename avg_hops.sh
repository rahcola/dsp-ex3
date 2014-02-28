#!/bin/bash

awk '{s+=$3;c+=1}END{print s/c}' -
