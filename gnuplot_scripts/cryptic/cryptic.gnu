#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set key font ",13"
set xtic font ",13"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key above


set term png
set output 'cryptic.png'
set grid back
set xtics rotate by -45
set xlabel "Month"
set ylabel "Number"
set boxwidth 1 relative
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
set y2tics
set y2range [10:20]
set y2label "Percentage"

plot "../Fig4/cryptic_vs_public.txt" using 1:3 t "Public notes" with boxes lc 'grey', \
     "../Fig4/cryptic_vs_public.txt" using 1:2 t "Cryptic notes" with boxes lc 'pink', \
     "../Fig4/cryptic_vs_public.txt" u 1:4 t "Percentage" w p lc -1 axes x1y2

EOFMarker
