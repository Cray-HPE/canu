# Lags

## ncn-m

- Lag number is the port of the primary switch connection to ncn-m:port 1.
- ncn-m:port 2, no lag

| Switch        | ncn-m                 | Lag   |
| ------------- | --------------------- | ----- |
| sw-leaf-001:1 | ncn-m001:ocp:1        | lag 1 |
| sw-leaf-001:2 | ncn-m002:ocp:1        | lag 2 |
| sw-leaf-002:1 | ncn-m001:pcie-slot1:1 | lag 1 |
| sw-leaf-002:2 | ncn-m002:pcie-slot1:1 | lag 2 |
| sw-leaf-003:1 | ncn-m003:ocp:1        | lag 1 |
| sw-leaf-004:1 | ncn-m003:pcie-slot1:1 | lag 1 |

## ncn-s

- Lag number is the port of the primary switch connection
- The connections to ocp:port1 and pcie:port1 slots on a ncn-s must be on the same lag across the primary and secondary switch
- The connections to ocp:port2 and pcie:port2 slots on a ncn-s must be on the same lag across the primary and secondary switch

| Switch        | ncn-m                 | Lag   |
| ------------- | --------------------- | ----- |
| sw-leaf-001:6 | ncn-s001:ocp:1        | lag 6 |
| sw-leaf-001:7 | ncn-s002:ocp:1        | lag 7 |
| sw-leaf-002:6 | ncn-s001:pcie-slot1:1 | lag 6 |
| sw-leaf-002:7 | ncn-s002:pcie-slot1:1 | lag 7 |
| sw-leaf-003:5 | ncn-s001:ocp:2        | lag 5 |
| sw-leaf-003:6 | ncn-s002:ocp:2        | lag 6 |
| sw-leaf-003:7 | ncn-s003:ocp:1        | lag 7 |
| sw-leaf-003:8 | ncn-s003:ocp:2        | lag 8 |
| sw-leaf-004:5 | ncn-s001:pcie-slot1:2 | lag 5 |
| sw-leaf-004:6 | ncn-s002:pcie-slot1:2 | lag 6 |
| sw-leaf-004:7 | ncn-s003:pcie-slot1:1 | lag 7 |
| sw-leaf-004:8 | ncn-s003:pcie-slot1:2 | lag 8 |

## ncn-w

- Lag number is the port of the primary switch connection to ncn-w

| Switch        | ncn-m          | Lag   |
| ------------- | -------------- | ----- |
| sw-leaf-001:3 | ncn-w001:ocp:1 | lag 3 |
| sw-leaf-001:4 | ncn-w002:ocp:1 | lag 4 |
| sw-leaf-002:3 | ncn-w001:ocp:2 | lag 3 |
| sw-leaf-002:4 | ncn-w002:ocp:2 | lag 4 |
| sw-leaf-003:2 | ncn-w004:ocp:1 | lag 2 |
| sw-leaf-004:2 | ncn-w004:ocp:2 | lag 2 |

## cec

- no lags

## cmm

- Lag number is the port of the primary switch connection to cmm

| Switch       | ncn-m    | Lag   |
| ------------ | -------- | ----- |
| sw-cdu-001:1 | cmm000:0 | lag 1 |
| sw-cdu-001:2 | cmm001:0 | lag 2 |
| sw-cdu-002:1 | cmm000:1 | lag 1 |
| sw-cdu-002:2 | cmm001:1 | lag 2 |

## uan

- Lag number is the port of the primary switch connection on uan:port 2
- The uan:port 1 connection has no lag

| Switch         | ncn-m               | Lag   |
| -------------- | ------------------- | ----- |
| sw-leaf-001:8  | uan001:ocp:1        | None  |
| sw-leaf-001:9  | uan002:ocp:1        | None  |
| sw-leaf-001:14 | uan001:ocp:2        | lag 8 |
| sw-leaf-001:15 | uan002:ocp:2        | lag 9 |
| sw-leaf-002:8  | uan001:pcie-slot1:1 | None  |
| sw-leaf-002:9  | uan002:pcie-slot1:1 | None  |
| sw-leaf-002:14 | uan001:pcie-slot1:2 | lag 8 |
| sw-leaf-002:15 | uan002:pcie-slot1:2 | lag 9 |

## sw-spine ==> sw-leaf

- Lag number is the digits of the primary leaf switch + 100

| Switch         | ncn-m          | Lag     |
| -------------- | -------------- | ------- |
| sw-spine-001:1 | sw-leaf-001:53 | lag 101 |
| sw-spine-001:2 | sw-leaf-002:53 | lag 101 |
| sw-spine-002:1 | sw-leaf-001:54 | lag 101 |
| sw-spine-002:2 | sw-leaf-002:54 | lag 101 |

## sw-spine ==> sw-leaf-bmc (TDS)

- Lag number is the digits of the leaf-bmc switch + 150

| Switch          | ncn-m              | Lag     |
| --------------- | ------------------ | ------- |
| sw-spine-001:48 | sw-leaf-bmc-001:49 | lag 151 |
| sw-spine-002:48 | sw-leaf-bmc-001:50 | lag 151 |

## sw-spine ==> sw-cdu

- Lag number is the digits of the primary cdu switch + 200

| Switch         | ncn-m         | Lag     |
| -------------- | ------------- | ------- |
| sw-spine-001:5 | sw-cdu-001:49 | lag 201 |
| sw-spine-001:6 | sw-cdu-002:49 | lag 201 |
| sw-spine-002:5 | sw-cdu-001:50 | lag 201 |
| sw-spine-002:6 | sw-cdu-002:50 | lag 201 |

## sw-spine ==> sw-spine

- Always lag 256

## sw-leaf ==> sw-spine

- Lag number is the digits of the primary spine switch + 100

| Switch         | ncn-m          | Lag     |
| -------------- | -------------- | ------- |
| sw-leaf-001:53 | sw-spine-001:1 | lag 101 |
| sw-leaf-001:54 | sw-spine-002:1 | lag 101 |
| sw-leaf-002:53 | sw-spine-001:2 | lag 101 |
| sw-leaf-002:54 | sw-spine-002:2 | lag 101 |

## sw-leaf ==> sw-leaf

- Always lag 256

## sw-leaf ==> sw-leaf-bmc

- Lag number is the digits of the leaf-bmc switch + 150

| Switch         | ncn-m              | Lag     |
| -------------- | ------------------ | ------- |
| sw-leaf-001:48 | sw-leaf-bmc-001:51 | lag 151 |
| sw-leaf-002:48 | sw-leaf-bmc-001:52 | lag 151 |

## sw-cdu ==> sw-spine

- Always lag 255

| Switch        | ncn-m          | Lag     |
| ------------- | -------------- | ------- |
| sw-cdu-001:49 | sw-spine-001:5 | lag 255 |
| sw-cdu-001:50 | sw-spine-002:5 | lag 255 |
| sw-cdu-002:49 | sw-spine-001:6 | lag 255 |
| sw-cdu-002:50 | sw-spine-002:6 | lag 255 |

## sw-cdu ==> sw-cdu

- Always lag 256

## sw-leaf-bmc ==> sw-spine (TDS)

- Always lag 255

| Switch             | ncn-m           | Lag     |
| ------------------ | --------------- | ------- |
| sw-leaf-bmc-001:49 | sw-spine-001:48 | lag 255 |
| sw-leaf-bmc-001:50 | sw-spine-002:48 | lag 255 |

## sw-leaf-bmc ==> sw-leaf

- Always lag 255

| Switch             | ncn-m          | Lag     |
| ------------------ | -------------- | ------- |
| sw-leaf-bmc-001:51 | sw-leaf-001:48 | lag 255 |
| sw-leaf-bmc-001:52 | sw-leaf-002:48 | lag 255 |
