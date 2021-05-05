#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set rmargin 20
set key font ",13"
set xtic font ",13"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key above


set term png
set output 'D1_cryptic.png'
set grid
set xtics rotate by -45
set xlabel "Month"
set ylabel "Number of monthly public Venmo transactions"
set boxwidth 1 relative
set style fill solid 1.0 border -1


plot "D1_cryptic.txt" using 3:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "Cryptic Notes" with boxes lc 3, \
     "D1_cryptic.txt" using 2:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "Non-cryptic Notes" with boxes lc 'grey', \

EOFMarker
