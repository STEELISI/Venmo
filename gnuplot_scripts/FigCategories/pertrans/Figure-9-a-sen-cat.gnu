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
set output 'D1_sen_categories.png'
set grid
set xtic rotate by -45
set xlabel "Each month in the dataset"
set ylabel "Number of Venmo notes month wise"
set boxwidth 0.8 relative
set style fill solid 1.0 border -1
set yrange [0:2100000]

plot "sen.txt" using 9:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S8LOC" with boxes lc 5, \
     "sen.txt" using 8:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S7REL" with boxes lc 6, \
     "sen.txt" using 7:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S4POL" with boxes lc 7, \
     "sen.txt" using 6:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S6VCR" with boxes lc 8, \
     "sen.txt" using 5:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S5RET" with boxes lc rgb "green", \
     "sen.txt" using 4:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S3DAG" with boxes lc rgb "blue", \
     "sen.txt" using 3:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S2HEA" with boxes lc rgb "pink", \
     "sen.txt" using 2:xticlabels(strstrt(strcol(1),'March')?strcol(1):'') t "S1ADU" with boxes lc rgb "grey", \

EOFMarker
