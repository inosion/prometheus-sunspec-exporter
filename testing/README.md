# Testing Notes

To test if your inveter supports SunSpec, 

Run the following 

```
docker build -t inosion/sunspec-test .
docker run --rm -ti -v `pwd`:/v --workdir /v inosion/sunspec-test python3 /src/pysunspec/scripts/suns.py -i 192.168.1.201

```
