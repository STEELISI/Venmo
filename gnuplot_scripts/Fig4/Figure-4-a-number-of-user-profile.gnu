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
set output 'Yearwise_Users_pub_vs_pri.png'
set grid
set xtics rotate by -45
set xlabel "Year"
set ylabel "Number of"
set boxwidth 0.7 absolute
set style fill solid 1.0 border -1

plot 'ipvp_users.txt' using 3:xtic(1) t "private Venmo users" with boxes lc 'gray', 'ipvp_users.txt' using 2:xtic(1) t "public Venmo users" with boxes lc 'pink'



EOFMarker
