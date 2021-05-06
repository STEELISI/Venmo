#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set key font ",12"
set xtics font ",12"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key abov

set term png
set output 'percentage_tsp.png'
set grid back

set xtics rotate by -45
set xlabel "Month"
set ylabel "Percentage"
set boxwidth 1.0 relative
set style rect fc lt -1 fs solid 0.15 noborder
set style fill solid 1 border -1
set obj rect from graph 0,0 to graph 0.70, 1 fc rgb "#aaaaaa" behind
set obj rect from graph 0.71,0 to graph 0.76, 1 fc rgb "#aaaaaa" behind
set obj rect from graph 0.87,0 to graph 0.99, 1 fc rgb "#aaaaaa" behind
set xdata time
set timefmt "%m-%Y"
set format x "%Y"
set label "D1" at graph 0.4, 0.95
set label "D2" at graph 0.71, 0.95
set label "D3" at graph 0.9, 0.95

plot 'percentage.txt' using 1:2 t "Sensitive/personal (percentage of total notes)" with boxes lc 'gray', 'percentage.txt' using 1:3 t "Sensitive/personal (percentage of English notes)" with boxes lc 'pink'

set output 'percentage_usp.png'
set y2label "Percentage"
set ylabel "Count"
set y2tics

plot 'users.txt' using 1:2 t "Total users" with boxes lc 'gray', '' u 1:3 t "Exposed users" with boxes lc 'pink', '' u 1:4 t "Percentage exposed" with points lc -1 axes x1y2

EOFMarker
