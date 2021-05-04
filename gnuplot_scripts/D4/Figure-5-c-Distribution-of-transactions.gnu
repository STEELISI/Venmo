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
set output 'D4_actual_transactions.png'
set grid
set xtics rotate by -45
set xlabel "Month"
set ylabel "Number of monthly public Venmo transactions"
set boxwidth 1 relative
set style fill solid 1.0 border -1


plot "monthly.txt" using 3:xtic(1) t "Total Notes" with boxes lc 'grey', \
     "monthly.txt" using 2:xtic(1) t "Notes in English" with boxes lc 3, \


EOFMarker
