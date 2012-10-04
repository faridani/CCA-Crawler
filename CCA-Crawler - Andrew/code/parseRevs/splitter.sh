#!/bin/sh

tail -n +2 deb_fin.csv > temp.csv
line_count=$(wc -l temp.csv | awk '{print $1}')
quart=$((line_count/4))
j=0
mkdir split_outs

h=$(head -n 1 deb_fin.csv)
for ((i=0;i<$line_count;i+=$quart));
do
	echo -n -e $h "\r\n" > split_outs/deb_fin.split$j.csv
	tail -n $(($line_count-$i)) temp.csv | head -n $quart >> split_outs/deb_fin.split$j.csv
	j=$(($j+1))
done

mv split_outs/deb_fin.split3.csv temp2.csv
cat temp2.csv split_outs/deb_fin.split4.csv > split_outs/deb_fin.split3.csv

#h=$(head -n 1 deb_fin.csv)
#for file in split_outs/deb_fin.split*.csv
#do
	#sed -i '1i'${h} $file
#done

rm -f temp.csv
rm -f temp2.csv
rm -f split_outs/deb_fin.split4.csv