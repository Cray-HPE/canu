# Logging and updates

Once the SHCD has run cleanly through CANU and CANU output has been manually validated, changes to the SHCD should be “committed” so that work is not lost, and other users can take advantage of the CANU changes.  

Add an entry to the changelog Config. Summary first worksheet.  The changelog should include: 

* The CANU command line used to validate the spreadsheet. 
* The CANU version being used to validate the spreadsheet. 
* An overview of changes made to the spreadsheet. 

After an SHCD has been validated it should be uploaded to an official storage location – customer communication (CAST ticket for customers) or SharePoint (internal systems and sometimes customer systems). 

After validation a Paddle or CCJ JSON file must be generated.  This file will be used instead of the SHCD for all subsequent operations.  To generate the Paddle/CCJ file use the previous `canu validate shcd` command and add the following to the end `--json –out <system name>-ccj.json`.  Using the above example the command would become: 

```text
canu validate shcd -a full --shcd ./HPE\ System\ Hela\ CCD.revA27.xlsx --tabs 10G_25G_40G_100G,NMN --corners I37,T107,J15,T16 --json --out hela-ccj.json  
```

[Back to index](index.md)