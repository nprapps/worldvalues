#!/bin/bash

echo "Import data"
./import.sh

echo "Summarize World Values"
./summarize_agreement.py
./summarize_questions.py > output/question_index.txt

