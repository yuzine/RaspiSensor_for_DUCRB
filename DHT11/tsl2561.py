#!/usr/bin/env python
# TSL2561 for Raspberry Pi

import smbus
import time

# refers to datasheet https://cdn-shop.adafruit.com/datasheets/TSL256x.pdf

BUS = 1
ADDR = 0x39

REG_CONTROL   = 0x80
REG_TIMING    = 0x81
REG_DATA0LOW  = 0x8C
REG_DATA0HIGH = 0x8D
REG_DATA1LOW  = 0x8E
REG_DATA1HIGH = 0x8F
REG_ID        = 0x8A

PART_TSL2561_CS      = 0x1
PART_TSL2561_T_FN_CL = 0x5

CONTROL_POWER_ON =  0x03
CONTROL_POWER_OFF = 0x00

TIMING = 0x2  # 402ms low gain(1X)


def setup():
    i2c = smbus.SMBus(BUS)
    part = i2c.read_byte_data(ADDR,REG_ID) >> 4
    # print "%d" % part
    i2c.write_byte_data(ADDR, REG_TIMING, TIMING)
    i2c.write_byte_data(ADDR, REG_CONTROL, CONTROL_POWER_ON)
    time.sleep(0.403)

    ch0low = i2c.read_byte_data(ADDR,REG_DATA0LOW)
    ch0high = i2c.read_byte_data(ADDR,REG_DATA0HIGH)
    ch1low = i2c.read_byte_data(ADDR,REG_DATA1LOW)
    ch1high = i2c.read_byte_data(ADDR,REG_DATA1HIGH)
    i2c.write_byte_data(ADDR, REG_CONTROL, CONTROL_POWER_OFF)
    
    ch0 = ch0high * 256 + ch0low
    ch1 = ch1high * 256 + ch1low

    return part, ch0, ch1

def calc_lux(part, int_ch0, int_ch1):
    ch0 = float(int_ch0 * 16)
    ch1 = float(int_ch1 * 16)

    if (ch0 == 0):
        return 0.0;

    if (part == PART_TSL2561_CS):
        if (ch1/ch0) <= 0.52:
            return 0.0315*ch0 - 0.0539*ch0*((ch1/ch0)**1.4)
        if (ch1/ch0) <= 0.65: 
            return 0.0229*ch0 - 0.0291*ch1
        if (ch1/ch0) <= 0.80: 
            return 0.0157*ch0 - 0.0180*ch1
        if (ch1/ch0) <= 1.30: 
            return 0.00338*ch0 - 0.00260*ch1
        return 0.0;
    else: 
        if (ch1/ch0) <= 0.50:
            return 0.0304*ch0 - 0.062*ch0*((ch1/ch0)**1.4)
        if (ch1/ch0) <= 0.61: 
            return 0.0224*ch0 - 0.031*ch1
        if (ch1/ch0) <= 0.80: 
            return 0.0128*ch0 - 0.0153*ch1
        if (ch1/ch0) <= 1.30: 
            return 0.00146*ch0 - 0.00112*ch1
        return 0.0;

#print "%.1f" % (calc_lux(part, ch0, ch1))

def getCalcLux():
    part, ch0, ch1 = setup()
    return calc_lux(part, ch0, ch1)
    
if __name__ == '__main__':
    try:
        getCalcLux()
    except KeyboardInterrupt:
        pass
