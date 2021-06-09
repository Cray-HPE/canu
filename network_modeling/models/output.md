# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

# HPE Cabling Standards and Descriptions- Shasta v1.4

Hardware Type: HPE

Software Version: Shasta v1.4


## NCN - MASTER

![master](images/hpe_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/hpe_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/hpe_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/hpe_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/hpe_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/hpe_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/hpe_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/hpe_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: ['HMN', 'NMN', 'CAN'] |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

#  Cabling Standards and Descriptions- Shasta v

Hardware Type: 

Software Version: Shasta v


## NCN - MASTER

![master](images/_master.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | Switch pair: switch 1 of 2 | VLANS: Manager 001 to site, otherwise NONE (see notes) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | Switch pair: switch 2 of 2 | VLANS: NONE |
| ILO | 1 | 1 | Master 001 connection to site, others HMN Leaf (see notes) | VLANS: HMN |

<br>
NOTES:

* REQUIRED:  Master 001 (ncn-m001) is required to have a site connection on OCP Port 2 for installation and maintenance.
* RECOMMENDED: Masters 002 and 003 may optionally have a site connection on OCP Port 2 for emergency system access.
* REQUIRED:  Master 001 (ncn-m001) is required to have it's BMC/iLO connected to the site.
<br>
<br>

## NCN - WORKER

![worker](images/_worker.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card is the default worker configuration.
<br>
<br>

## NCN - WORKER TWO CARD (OPTION)

![worker_two_card_(option)](images/_worker_two_card_(option).png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | NONE | VLANS: NONE |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | NONE | VLANS: NONE |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* A single OCP card and a second PCIE card in Slot 1 is an optional worker configuration when more resiliency is desired.
<br>
<br>

## NCN - STORAGE

![storage](images/_storage.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: ['HMN', 'NMN', 'CAN'] |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: SUN (cabled but not configured) |
| PCIE-SLOT1 | 1 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: SUN (cabled but not configured) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* OCP Port 1 and PCIE Slot 1 Port 1 (first ports) are bonded for the NMN, HMN and CAN.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) cabled but not configured in this release.
<br>
<br>

## APPLICATION - UAN

![uan](images/_uan.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NMN |
| OCP | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| PCIE-SLOT1 | 1 | 25 | switch pair: switch 1 of 2 | VLANS: NONE |
| PCIE-SLOT1 | 2 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: CAN |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
NOTES:

* All ports are cabled.
* The OCP Port 1 connects to the NMN in a non-bonded configuration.
* The PCIE Slot 1 Port 1 is cabled but not configured/used in this release.
* OCP Port 2 and PCIE Slot 1 Port 2 (second ports) are bonded for the CAN.
<br>
<br>

## APPLICATION - LOGIN

![login](images/_login.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| OCP | 1 | 25 | MLAG switch pair: switch 1 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| OCP | 2 | 25 | MLAG switch pair: switch 2 of 2 | VLANS: HMN, NMN, CAN (e.g. bond0) |
| ILO | 1 | 1 | HMN Leaf | VLANS: HMN |

<br>
<br>

## MOUNTAIN - CMM

![cmm](images/_cmm.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CMM | 1 | 10 | Static LAG: CDU switch 1 of 2 | VLANS: Per cabinet NMN and HMN |
| CMM | 2 | 10 | Static LAG: CDU switch 2 of 2 | VLANS: Per cabinet NMN and HMN |

<br>
<br>

## MOUNTAIN - CEC

![cec](images/_cec.png)

| Device | Port | Speed | Destination Network Port | Use / Configuration |
|:-------|------|-------|:-------------------------|:--------------------|
| CEC | 1 | 0.1 | CDU switch access port | VLANS: per cabinet HMN? |

<br>
<br>

Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
Error: Library prettydiff.beautify.markdown does not exist.
