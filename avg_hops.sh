#!/bin/bash

# Jani Rahkola, 013606996

awk '{s+=$3;c+=1}END{print s/c}' -
