#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set rmargin 5
set key font ",14"
set xtics font ",14"
set ytics font ",14"
set xlabel font ",14"
set ylabel font ",14"
set key abov

set term png
set output 'pub_vs_pri_trans.png'
set grid
set xtics rotate by -45
set xlabel "Year"
set ylabel "Percentage of"
set boxwidth 0.7 absolute
set style fill solid 1.0 border -1
set yrange [0:101]


plot 'per_ipvp_trans.txt' using 3:xtic(1) t "private Venmo transactions" with boxes lc 'gray', 'per_ipvp_trans.txt' using 2:xtic(1) t "public Venmo transactions" with boxes lc 'pink'



EOFMarker
