# HPE Cabling Standards and Descriptions- CSM v1.0

Hardware Type: HPE

Software Version: CSM v1.0


## NCN - MASTER

![master](./images/hpe_master.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| OCP | 1 | primary (first switch in MLAG pair) |  mgmt0 |  HMN, NMN, CAN  |  MLAG-LACP |
| OCP | 2 | site |  Manager 001 to site, otherwise NONE (see notes) |  N/A  |  N/A |
| PCIE-SLOT1 | 1 | secondary (second switch in MLAG pair) |  mgmt1 |  HMN, NMN, CAN  |  MLAG-LACP |
| PCIE-SLOT1 | 2 | None |  N/A |  N/A  |  N/A |
| ILO | 1 | HMN Leaf |  N/A |  HMN  |  N/A |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](./images/hpe_worker.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| OCP | 1 | primary (first switch in MLAG pair) |  mgmt0 |  HMN, NMN, CAN  |  MLAG-LACP |
| OCP | 2 | secondary (second switch in MLAG pair) |  mgmt1 |  HMN, NMN, CAN  |  MLAG-LACP |
| ILO | 1 | HMN Leaf |  N/A |  HMN  |  N/A |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - STORAGE

![storage](./images/hpe_storage.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| OCP | 1 | primary (first switch in MLAG pair) |  mgmt0 |  HMN, NMN, CAN  |  MLAG-LACP |
| OCP | 2 | primary (first switch in MLAG pair) |  mgmt1 |  SUN  |  MLAG-LACP |
| PCIE-SLOT1 | 1 | secondary (second switch in MLAG pair) |  mgmt2 |  HMN, NMN, CAN  |  MLAG-LACP |
| PCIE-SLOT1 | 2 | secondary (second switch in MLAG pair) |  mgmt3 |  SUN  |  MLAG-LACP |
| ILO | 1 | HMN Leaf |  N/A |  HMN  |  N/A |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](./images/hpe_uan.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| OCP | 1 | primary (first switch in MLAG pair) |  N/A |  NMN  |  N/A |
| OCP | 2 | primary (first switch in MLAG pair) |  N/A |  CAN  |  MLAG-LACP |
| PCIE-SLOT1 | 1 | secondary (second switch in MLAG pair) |  N/A |  N/A  |  N/A |
| PCIE-SLOT1 | 2 | secondary (second switch in MLAG pair) |  N/A |  CAN  |  MLAG-LACP |
| ILO | 1 | HMN Leaf |  N/A |  HMN  |  N/A |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](./images/hpe_login.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| OCP | 1 | primary (first switch in MLAG pair) |  N/A |  HMN, NMN, CAN  |  MLAG-LACP |
| OCP | 2 | secondary (second switch in MLAG pair) |  N/A |  HMN, NMN, CAN  |  MLAG-LACP |
| ILO | 1 | HMN Leaf |  N/A |  HMN  |  N/A |

<br>
<br>

## MOUNTAIN - CMM

![cmm](./images/hpe_cmm.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| CMM | 1 | primary (first switch in MLAG pair) |  N/A |  MTN_HMN, MTN_NMN  |  MLAG-STATIC |
| CMM | 2 | secondary (second switch in MLAG pair) |  N/A |  MTN_HMN, MTN_NMN  |  MLAG-STATIC |

<br>
<br>

## MOUNTAIN - CEC

![cec](./images/hpe_cec.png)

| Device | Port | Destination | Name | VLAN | LAG |
|:-------|------|:-------------------------|:--------------|:--------------------|:-----|
| CEC | 1 | CDU switch access port |  N/A |  MTN_HMN  |  N/A |

<br>
<br>
