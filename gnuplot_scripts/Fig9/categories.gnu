#!/bin/bash
minval=0    # the result of some (omitted calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
#set style fill border -1
#set multiplot layout 2,1
set key font ",13"
set xtic font ",13"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key above
set xdata time
set timefmt "%m-%Y"
set format x "%Y"

set term png
set output 'sen_categories.png'
set grid back
set xtic rotate by -45
set xlabel "Month"
set ylabel "Number"
set boxwidth 0.8 relative
set style fill solid 1.0 border -1
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


plot "monthly.txt" using 1:9 t "S8LOC" with boxes lc 5, \
     "monthly.txt" using 1:8 t "S7REL" with boxes lc 6, \
     "monthly.txt" using 1:7 t "S4POL" with boxes lc 7, \
     "monthly.txt" using 1:6 t "S6VCR" with boxes lc 8, \
     "monthly.txt" using 1:5 t "S5RET" with boxes lc rgb "green", \
     "monthly.txt" using 1:4 t "S3DAG" with boxes lc rgb "blue", \
     "monthly.txt" using 1:3 t "S2HEA" with boxes lc rgb "pink", \
     "monthly.txt" using 1:2 t "S1ADU" with boxes lc rgb "grey", \

set output 'per_categories.png'

plot "per.txt" using 1:4 t "P4ADD" with boxes lc 5, \
     "per.txt" using 1:6 t "P3PHO" with boxes lc 8, \
     "per.txt" using 1:5 t "P5PAD" with boxes lc 2, \
     "per.txt" using 1:3 t "P2EMA" with boxes lc 3, \
     "per.txt" using 1:2 t "P1ACC" with boxes lc 4, \

EOFMarker
