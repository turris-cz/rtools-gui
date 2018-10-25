#!/bin/sh

# For testers
for i in $(seq 0 3); do
	barcode -S -o "tester-$i.svg" -e code128 -b "$(perl -e "print 0xFFFFFFFF0000000$i")"
done

for i in $(seq 30 36); do
	barcode -S -o "board-$i.svg" -e code128 -b "$(perl -e "print 0x0000000D${i}000000")"
done
