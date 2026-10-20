#!/bin/sh
# health.sh URL — prints UP or DOWN, exits 0 or 1.
# Chapter 10's health-check recipe: -f makes HTTP errors fail,
# --max-time keeps a hung service from hanging the checker.
if curl -fsS --max-time 5 "$1" -o /dev/null 2>/dev/null; then
    echo "UP   $1"
else
    echo "DOWN $1"
    exit 1
fi
