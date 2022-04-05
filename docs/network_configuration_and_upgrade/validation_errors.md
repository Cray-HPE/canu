# Typical CANU validation errors and how to fix them

**Issue:**  Port number not specified

	validate_shcd - CRITICAL: A port number must be specified. Please correct the SHCD for HMN:V36 with an empty value 

**Solution:** 	

Blank cell.  Minimally the Source or Destination and Port needs to be specified. 

**Issue:**  PDU tab not found from SHCD

	Tab PDU not found in ./HPE System Hela CCD.revA27.xlsx 

	Available tabs: ['Config. Summary', 'HPE Cables', 'RiverRackLayout ', 
	'Arista', 'River Device Diagrams', 'HPE Devices', 'SCT pt_pt'
	'yaml', 'Mountain-TDS-Management', 'MTN Rack Layout', 
	'10G_25G_40G_100G', 'NMN', 'HMN', 'PDU '] 

**SOLUTION:**  	

PDU has an extra space in the tab name. 

**Issue:**  Incorrectly formatted header in SHCD

	validate_shcd - CRITICAL:  
	
	On tab PDU, the header is formatted incorrectly. 
	
	Columns must exist in the following order, but may have other columns in between: 
	
	[0, 1, 2, 'Slot', 'Port', 'Destination', 'Rack', 'Location', 'Port'] 
	
**SOLUTION:** 

Fix the header naming to match the expected output. 

[Back to index](index.md)