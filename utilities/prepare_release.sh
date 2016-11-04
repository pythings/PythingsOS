#!/bin/bash
rm -f files.txt
python utilities/create_files_list.py > files.txt
python utilities/create_files_list.py > /tmp/pythings_files.txt
mv /tmp/pythings_files.txt files.txt
python utilities/create_files_list.py > /tmp/pythings_files.txt
mv /tmp/pythings_files.txt files.txt

echo -n "$1" > version
