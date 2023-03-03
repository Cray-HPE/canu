# Paddle / CCJ File

The **paddle** or **CCJ** (CSM Cabling JSON) is a JSON representation of the network. There are many benefits of using the CCJ:

- The CCJ schema has been validated using `paddle-schema.json`
- The paddle has been architecturally validated to ensure all connections between devices are approved
- All port connections between devices have been checked using the CANU model to ensure speed, slot choice, and port availability has been confirmed
- The CCJ is machine-readable and therefore easy to build additional tooling around
- Less flags need to be used when reading the CCJ vs the SHCD

The SHCD can easily be converted into CCJ by using

  ```bash
  canu validate shcd --shcd SHCD.xlsx --json --out paddle.json
  ```
