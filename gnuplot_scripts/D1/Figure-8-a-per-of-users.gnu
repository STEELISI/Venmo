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
set output 'percentage_users_affected.png'
set grid
set xtics rotate by -45
set xlabel "Each month in the dataset"
set ylabel "Percentage of monthly public Venmo users"
set boxwidth 0.5 relative
set style fill solid 1.0 border -1
set yrange [0:101]
set ytics 10

plot 'usr_percentage.txt' using 5:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "Other users" with boxes lc 'gray', 'usr_percentage.txt' using 4:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "Users affected" with boxes lc 6

EOFMarker
