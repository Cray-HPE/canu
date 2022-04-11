# Collect Data

* Retrieve the most up-to-date SHCD spreadsheet. Accuracy in this spreadsheet is critical.

* Retrieve SLS file from a Shasta system (log in to ncn-m001) on a NCN, this will output the sls file to a file called sls_file.json in your current working directory.

```text
cray sls dumpstate list  --format json >> sls_file.json
```

* Retrieve switch running configs (log in to ncn-m001)

Log into the management network switches, you can get the ips/hostnames by running this command on a NCN:

```text
cat /etc/hosts | grep sw-
```

If /etc/hosts is not available because the system is being installed you will be on the pit and will need to run:

```text
cat /var/www/ephemeral/prep/redbull/sls_input_file.json | jq ‘.Networks | .HMN | .ExtraProperties.Subnets | .[] | select(.Name==“network_hardware”)'
```

Run the script below to automatically collect all switch configs.  If the command fails then log in to each individual switch and run 'show run'.

```text
canu backup network --sls-file sls_input_file.json --network HMN --folder running
```

NOTE: --network CMN / HMN
    * CMN = connecting from external network
    * HMN = connecting from internal network

* (optional): Retrieve customizations file. (log in from ncn-m001)

```text
kubectl -n loftsman get secret site-init -o json | jq -r '.data."customizations.yaml"' | base64 -d > customizations.yaml
```

This will output the customizations file to a file called customizations.yaml in your current working directory.

[Back to index](index.md)