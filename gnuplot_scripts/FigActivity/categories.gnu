#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set yrange [1:40000000]
set boxwidth 0.9 absolute
set datafile missing '-'
set rmargin 10
set key font ",12"
set xtics font ",12"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
#set key abov left
#set key Left abov
set key Left abov reverse


set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from graph 0,0 to graph 0.38, 1 fc rgb "#aaaaaa" behind
set obj rect from graph 0.41,0 to graph 0.62, 1 fc rgb "#aaaaaa" behind
set obj rect from graph 0.65,0 to graph 0.99, 1 fc rgb "#aaaaaa" behind
set term png
set output 'users_uc.png'
set grid
#set xdata time
#set timefmt "%m/%d/%y"
set xtics rotate by -90
set logscale y
set label "D1" at graph 0.18, 0.95
set label "D2" at graph 0.5, 0.95
set label "D3" at graph 0.8, 0.95
set xlabel "User category based on the range of total notes posted"
set ylabel "Number"
set style fill solid 0.8 border -1
set ytics 10
set y2tics
set y2label "Percentage"
plot 'counts.txt' u 3:xtic(1) lc 'grey' w boxes t "Total users", '' u 2:xtic(1) w boxes ti "Users w sensitive/personal notes" lc 'pink', '' u 4:xtic(1) w linespoints axes x1y2 ti "Affected users" lc -1
set output "trans_uc.png"
set yrange [1:1000000000]
set y2range [8:15]
plot 'counts.txt' u 6:xtic(1) lc 'grey' w boxes t "Total notes", '' u 5:xtic(1) w boxes ti "Sensitive/personal notes" lc 'pink', '' u 7:xtic(1) w lp axes x1y2 ti "Percentage notes" lc -1
#'percentage_uc.txt' using 3: xtic(1) t "Total users" with histogram lc 10, 'percentage_uc.txt' using 2: xtic(1) t "Users who posted at least 1 sensitive/personal note" with histogram lc 3, 'percentage_uc.txt' using 6: xtic(1) t "Total notes" with histogram lc 5, 'percentage_uc.txt' using 5: xtic(1) t "Sensitive/personal notes" with histogram lc 7




EOFMarker
