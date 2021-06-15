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
set output 'senu_categories.png'
set grid back
set xtic rotate by -45
set xlabel "Year"
set ylabel "Number"
set y2label "Percentage"
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
set label "counts" at graph 0.5, 0.65
set label "percentages" at graph 0.5, 0.5
set y2tics
set logscale y
set yrange [0:]
set y2range [0:]

plot "sensitive.txt" using 1:((\$9-\$8)/\$10*100) t "S8LOC" with linespoints lc 1  axes x1y2, "sensitive.txt" using 1:((\$9-\$8)) notitle  with lines lc 1, \
     "sensitive.txt" using 1:((\$8-\$7)/\$10*100) t "S7REL" with linespoints lc 6 axes x1y2,  "sensitive.txt" using 1:((\$8-\$7)/1) notitle with lines lc 6, \
     "sensitive.txt" using 1:((\$6-\$5)/\$10*100) t "S6VCR" with lp lc 8 axes x1y2,  "sensitive.txt" using 1:((\$6-\$5)/1) notitle with l lc 8, \
     "sensitive.txt" using 1:((\$5-\$4)/\$10*100) t "S5RET" with lp lc rgb "green" axes x1y2, "sensitive.txt" using 1:((\$5-\$4)/1) notitle with l lc rgb "green", \
     "sensitive.txt" using 1:((\$7-\$6)/\$10*100) t "S4POL" with linespoints lc 7 axes x1y2, "sensitive.txt" using 1:((\$7-\$6)/1) notitle with lines lc 7, \
     "sensitive.txt" using 1:((\$4-\$3)/\$10*100) t "S3DAG" with lp lc rgb "blue" axes x1y2, "sensitive.txt" using 1:((\$4-\$3)/1) notitle with l lc rgb "blue",  \
     "sensitive.txt" using 1:((\$3-\$2)/\$10*100) t "S2HEA" with lp lc rgb "pink" axes x1y2,  "sensitive.txt" using 1:((\$3-\$2)/1) notitle with l lc rgb "pink", \
     "sensitive.txt" using 1:(\$2/\$10*100) t "S1ADU" with lp lc rgb "grey" axes x1y2, "sensitive.txt" using 1:(\$2/1) notitle with l lc rgb "grey" \

set output 'peru_categories.png'
unset label 4
unset label 5
set label "counts" at graph 0.5, 0.45
set label "percentages" at graph 0.5, 0.1

plot "personal.txt" using 1:((\$4-\$3)/\$7*100) t "P5PAD" with linespoints lc 2 axes x1y2,  "personal.txt" using 1:((\$4-\$3)) notitle with lines lc 2, \
     "personal.txt" using 1:((\$6-\$5)/\$7*100) t "P4ADD" with linespoints lc 1 axes x1y2, "personal.txt" using 1:((\$6-\$5)) notitle with lines lc 1, \
     "personal.txt" using 1:((\$5-\$4)/\$7*100) t "P3PHO" with linespoints lc 8 axes x1y2, "personal.txt" using 1:((\$5-\$4)) notitle with lines lc 8, \
     "personal.txt" using 1:((\$3-\$2)/\$7*100) t "P2EMA" with linespoints lc 3 axes x1y2,  "personal.txt" using 1:((\$3-\$2)) notitle with lines lc 3, \
     "personal.txt" using 1:((\$2)/\$7*100) t "P1ACC" with linespoints lc 4 axes x1y2, "personal.txt" using 1:((\$2)) notitle with lines lc 4 \

EOFMarker
