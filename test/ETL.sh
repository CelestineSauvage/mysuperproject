#Extract
echo "python3 ../src/data_download.py ../downloads/TEST/APEC_TEST  --publieeDepuis jour"
python3 src/data_download.py downloads/TEST/APEC_TEST  --publieeDepuis jour

echo "python3 ../src/data_download.py downloads/TEST/FT_TEST  department 18 --publieeDepuis 1"
python3 src/data_download.py downloads/TEST/FT_TEST --publieeDepuis 1

#Transform

python3 src/data_transform.py downloads/TEST/APEC_TEST 1

python3 src/data_transform.py downloads/TEST/FT_TEST 0


# Load

python3 src/load_data_into_db.py downloads/TEST/FT_TEST 