# Testing Notes

To test if your inveter supports SunSpec, 

Run the following 

```
docker build -t inosion/sunspec-test .
# Test an IP, with target modbus address of 126
docker run --rm -ti  inosion/sunspec-test python3 /src/pysunspec/scripts/suns.py -i 192.168.1.40 -a 126
```
