#!/bin/bash

echo "Create database"
dropdb --if-exists worldvalues
createdb worldvalues

echo "Convert codebook from xls to csv format"
in2csv data/WV6_Codebook_v_2014_11_07.xls > data/codebook_raw.csv
tail -n +4 data/codebook_raw.csv > data/codebook.csv

echo "Import World Values data"
./import.py

echo "psql copy"
psql worldvalues -c "COPY survey_responses FROM '`pwd`/data/WV6_Data_r_v_2015_04_18-clean.csv' DELIMITER ',' CSV HEADER;"



