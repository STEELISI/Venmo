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
set output 'D2_actual_transactions.png'
set grid
set xtics rotate by -45
set xlabel "Month"
set ylabel "Number of monthly public Venmo transactions"
set boxwidth 2.0 relative
set style fill solid 1.0 border -1

plot "actual_transactions_mon.txt" using 2:xtic(1) t "Total Notes" with histogram lc 'grey', \
     "actual_transactions_mon.txt" using 3:xtic(1) t "Notes in English" with histogram lc 3, \


EOFMarker
