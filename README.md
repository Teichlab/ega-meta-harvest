# Retrieve Sanger IDs and library type per EGAF

The repository houses a simple Python script that queries EGA metadata for any given dataset (EGAD), getting a master list of its files (EGAF) and for each of those retrieving the matching sample (EGAN) and experiment (EGAX) information. It's necessary to perform this as for any given file, we need to find its Sanger ID (lives in EGAN metadata, seems to be `title`/`subject_id` in the current upload schema) and library type (lives in EGAX metadata as `library_construction_protocol`).

Why bother with this? Go take a look at `parsed/EGAD00001015679.csv` and look for the Sanger ID `COV19_CH_214527346`. You will see four separate EGAFs, of which two are flagged as TCR and two are flagged as BCR.

The script exists because it's impossible to reconstruct an EGAF to EGAX relationship from the pre-parsed forms of metadata EGA offers per dataset. Upon gaining access to new EGA datasets, it should be a pretty quick process to run the metadata parsing (about 10 files analysed per second), and the results can be stored for later access as needed. Easier to find a Sanger ID in a vacuum by searching some CSV files.

Running the script requires the EGAD to parse:

```python
python3 parse_egad.py EGAD00001015679
```

This created the aforementioned `parsed/EGAD00001015679.csv` file.

A quick grep to find a Sanger ID in the collected CSVs, getting the EGAFs and library types:

```bash
$ $ grep -h "COV19_CH_214527346" parsed/*.csv | cut -f 1,11 -d ","
EGAF00008701867,Chromium single cell TCR
EGAF00008701885,Chromium single cell TCR
EGAF00008887639,Chromium single cell BCR
EGAF00008887657,Chromium single cell BCR
```