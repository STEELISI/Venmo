#!/bin/bash
minval=0    # the result of some (omitted calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
#set style fill border -1
#set multiplot layout 2,1
set rmargin 20
set key font ",13"
set xtic font ",13"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key above


set term png
set output 'D1_per_categories.png'
set grid
set xtic rotate by -45
set xlabel "Each month in the dataset"
#set ylabel "Number of Venmo users affected monthly"
set ylabel "Number of Venmo notes month wise"
set boxwidth 0.8 relative
set style fill solid 0.7 border -1
#set key top 
#set yrange [0:2100000]
#set xtic ("6/1/12","6/12/12"
#set xtic 10
#set autoscale
#AC E I PH AD
plot "per.txt" using 4:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "P4ADD" with boxes lc 5, \
     "per.txt" using 6:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "P3PHO" with boxes lc 8, \
     "per.txt" using 5:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "P5PAD" with boxes lc 2, \
     "per.txt" using 3:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "P2EMA" with boxes lc 3, \
     "per.txt" using 2:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "P1ACC" with boxes lc 4, \

EOFMarker
