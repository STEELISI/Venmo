#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set rmargin 20
set key font ",12"
set xtics font ",12"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key abov

set term png
set output 'percentage.png'
set grid
set xtics rotate by -45
set xlabel "Each month in the dataset"
set ylabel "Percentage of monthly public Venmo transaction notes"
set boxwidth 1.0 relative
set style fill solid 1.0 border -1
set yrange [0:35]
set ytics 10

plot '6-a.txt' using 2:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "Percentage of sensitive/personal notes (Notes in English)" with boxes lc 2, '6-a.txt' using 3:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "Percentage of sensitive/personal notes (Total Notes)" with boxes lc 7



EOFMarker
