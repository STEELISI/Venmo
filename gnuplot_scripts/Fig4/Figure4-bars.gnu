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
set y2tics
set key above

set term png
set output 'Users-bars.png'
set grid
set xtics rotate by -45
set xlabel "Year"
set ylabel "Number"
set y2label "Percentage"
set boxwidth 0.7 absolute
set style fill solid 1.0 border -1

plot 'ipvp_users.txt' using 3:xtic(1) t "private Venmo users" with boxes lc 'gray', 'ipvp_users.txt' using 2:xtic(1) t "public Venmo users" with boxes lc 'pink', 'ppvp.txt' u (100-\$2):xtic(1) w lp axes x1y2 t 'percentage private' lc -1                                                                                                       

set output 'Trans-bars.png'


plot 'ipvp_trans.txt' using 3:xtic(1) t "private Venmo transactions" with boxes lc 'gray', 'ipvp_trans.txt' using 2:xtic(1) t "public Venmo transactions" with boxes lc 'pink', 'per_ipvp_trans.txt' u (100-\$2):xtic(1) w lp axes x1y2 t 'percentage private' lc -1                                                                                                       

EOFMarker


