import requests
import pandas as pd
import time
import sys

#run with dataset ID (EGAD) as the positional argument
egad = sys.argv[1]

#a function to try to hit the server again if the connection gives out
def retry_get(url, retries=5):
    #try to hit the URL a specified number of times
    for i in range(retries):
        try:
            response = requests.get(url)
            #apparently necessary to check that the request went through okay before json
            #http://requests.readthedocs.io/en/latest/user/quickstart/
            response.raise_for_status()
            #we're here, we didn't fail, we're good! we care about the json
            return response.json()
        except:
            #the get bricked, try again in a second
            time.sleep(1)
    #we tried a few times and failed, shut it down
    raise RuntimeError("Failed to get "+url)

#get master list of EGAFs (files) for the dataset
egafs = retry_get("https://metadata.ega-archive.org/datasets/"+egad+"/files")
#helper variable for parsed stuff in dict form as we move along
egaf_dicts = []
#this is a list of dicts for each EGAF
#the field we care about is accession_id, which is the actual EGAF identifier
for ind, egaf in enumerate([i["accession_id"] for i in egafs]):
    #progress report as this can take a while
    if ind % 50 == 0:
        print(ind)
    #need to pull the corresponding EGAN (sample), to get sanger ID
    egans = retry_get("https://metadata.ega-archive.org/files/"+egaf+"/samples")
    #and EGAX (experiment), to get the library type
    #which is important in cases of some sanger IDs with multiple libraries
    egaxs = retry_get("https://metadata.ega-archive.org/files/"+egaf+"/experiments")
    #both of these should be length 1, otherwise it's some weird file to skip
    if len(egans) != 1:
        print("Non-one EGAN count for "+egaf+", skipping")
        continue
    if len(egaxs) != 1:
        print("Non-one EGAX count for "+egaf+", skipping")
        continue
    #extract our actual entry for both
    egan = egans[0]
    egax = egaxs[0]
    #both of these have an accession_id field, which will create conflicts
    #rename (by popping the old value into a new key)
    egan["egan_accession_id"] = egan.pop("accession_id")
    egax["egax_accession_id"] = egax.pop("accession_id")
    #can combine the dicts now
    egaf_dicts.append({"egaf_accession_id":egaf, **egan, **egax})

#we can now turn this to a data frame and save it
df = pd.DataFrame.from_records(egaf_dicts, index="egaf_accession_id")
df.to_csv("parsed/"+egad+".csv")
