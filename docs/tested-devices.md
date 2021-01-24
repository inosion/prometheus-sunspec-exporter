# Known Working / Tested Devices

Search (Sunspec Modbus Certified List)[https://sunspec.org/sunspec-modbus-certified-products/] for your device.

Because Sunspec is a standard, the configuration required, for the exporter, will vary only:

1. Which Modbus address the device listens on
2. The `model_ids` you need from the device (don't need the serial number 6 times a minute :-) )
3. Any custom filterng required

You won't need to map any data fields, the exporter does all that work.

# Devices Working

   |--------------|----------------------------|--------------------------------------------------------|---------------|
   | Manufacturer | Model                      | Notes                                                  | Sample Config |
   |--------------|----------------------------|--------------------------------------------------------|---------------|
   | SMA          | SunnyBoy TriPower STL-6000 | Address 126 (add 123 to the base SMA address)          |               |
   |              |                            | Filter required for Amps at night; NaN map to Zero (0) |               |
   | SunSpec      |                            | Works out of the box (Fronius Modbus IS Sunspec)       |               |
