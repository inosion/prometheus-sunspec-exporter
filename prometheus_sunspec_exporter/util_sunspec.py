import sunspec.core.client as client
import sunspec.core.suns as suns
try:
    import xml.etree.ElementTree as ET
except:
    import elementtree.ElementTree as ET
import sunspec.core.pics as pics
import sunspec.core.util as util
from xml.dom import minidom
import time 



def model_name(model):
    
    """Model Data Name"""

    if model.model_type.label:
        label = '%s (%s)' % (model.model_type.label, str(model.id))
    else:
        label = '(%s)' % (str(model.id))
    return label

def sunspec_test(ip, port, address):

    """
    Original suns options:

        -o: output mode for data (text, xml)
        -x: export model description (slang, xml)
        -t: transport type: tcp or rtu (default: tcp)
        -a: modbus slave address (default: 1)
        -i: ip address to use for modbus tcp (default: localhost)
        -P: port number for modbus tcp (default: 502)
        -p: serial port for modbus rtu (default: /dev/ttyUSB0)
        -b: baud rate for modbus rtu (default: 9600)
        -T: timeout, in seconds (can be fractional, such as 1.5; default: 2.0)
        -r: number of retries attempted for each modbus read
        -m: specify model file
        -M: specify directory containing model files
        -s: run as a test server
        -I: logger id (for sunspec logger xml output)
        -N: logger id namespace (for sunspec logger xml output, defaults to 'mac')
        -l: limit number of registers requested in a single read (max is 125)
        -c: check models for internal consistency then exit
        -v: verbose level (up to -vvvv for most verbose)
        -V: print current release number and exit
    """


    try:
        sd = client.SunSpecClientDevice(client.TCP, address, ipaddr=ip, ipport=port, timeout=10.0)

    except client.SunSpecClientError as e:
        print('Error: %s' % (e))
        sys.exit(1)

    if sd is not None:

        print( '\nTimestamp: %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))

        # read all models in the device
        sd.read()

        root = ET.Element(pics.PICS_ROOT)
        sd.device.to_pics(parent = root, single_repeating = True)
        print(minidom.parseString(ET.tostring(root)).toprettyxml(indent="  "))

        for model in sd.device.models_list:
            if model.model_type.label:
                label = '%s (%s)' % (model.model_type.label, str(model.id))
            else:
                label = '(%s)' % (str(model.id))
            print('\nmodel: %s\n' % (label))
            for block in model.blocks:
                if block.index > 0:
                  index = '%02d:' % (block.index)
                else:
                  index = '   '
                for point in block.points_list:
                    if point.value is not None:
                        if point.point_type.label:
                            label = '   %s%s (%s):' % (index, point.point_type.label, point.point_type.id)
                        else:
                            label = '   %s(%s):' % (index, point.point_type.id)
                        units = point.point_type.units
                        if units is None:
                            units = ''
                        if point.point_type.type == suns.SUNS_TYPE_BITFIELD16:
                            value = '0x%04x' % (point.value)
                        elif point.point_type.type == suns.SUNS_TYPE_BITFIELD32:
                            value = '0x%08x' % (point.value)
                        else:
                            value = str(point.value).rstrip('\0')
                        print('%-40s %20s %-10s' % (label, value, str(units)))
