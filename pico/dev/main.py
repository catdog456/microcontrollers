#TinyML demo

#capture signal from radio and categorise with tiny ML

# Watch this video for more information about nRF24L01 library https://www.youtube.com/watch?v=aP8rSN-1eT0


import json

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

from machine import SPI, Pin, I2C

if config["use_imu"] == True:
    from imu import MPU6050
    i2c0 = I2C(0, sda=Pin(config["pin_imu_sda"]), scl=Pin(config["pin_imu_scl"]), freq=400000)
    imu = MPU6050(i2c0)
    print(i2c0.scan())

if config["use_oled"] == True:
    from ssd1306 import SSD1306_I2C
    i2c1=machine.I2C(1,sda=Pin(config["pin_oled_sda"]), scl=Pin(config["pin_oled_scl"]), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c1)
    print(i2c1.scan())
    def showmessage(strings): # strings- an array of text lines
        oled.fill(0)
        oled.text(str(ax),5,0)
        oled.text(str(ay),5,10)
        oled.text(str(az),5,20)
        oled.text(str(gx),5,30)
        oled.text(str(gy),5,40)
        oled.text(str(gz),5,50)
        oled.text(str(tem),50,35)
        oled.text(str(role),60,0)
        oled.show()
    
if config["use_nrf"] == True:
    from nrf24l01 import NRF24L01
    csn = Pin(config["pin_nrf_csn"], mode=Pin.OUT, value=1) # Chip Select Not
    ce = Pin(config["pin_nrf_ce"], mode=Pin.OUT, value=0)  # Chip Enable
    payload_size = 20

    # Define the channel or 'pipes' the radios use.
    # switch round the pipes depending if this is a sender or receiver pico
    if config["role"] == "send":
        send_pipe = b"\xe1\xf0\xf0\xf0\xf0"
        receive_pipe = b"\xd2\xf0\xf0\xf0\xf0"
    else:
        send_pipe = b"\xd2\xf0\xf0\xf0\xf0"
        receive_pipe = b"\xe1\xf0\xf0\xf0\xf0"
    def setup():
        print("Initialising the nRF24L0+ Module")
        nrf = NRF24L01(SPI(0), csn, ce, payload_size=payload_size)
        nrf.open_tx_pipe(send_pipe)
        nrf.open_rx_pipe(1, receive_pipe)
        nrf.start_listening()
        return nrf
    def send(nrf, msg):
        print("sending message.", msg)
        nrf.stop_listening()
        try:
            for n in range(len(msg)):
                try:
                    encoded_string = msg[n].encode()
                    byte_array = bytearray(encoded_string)
                    buf = struct.pack("s", byte_array)
                    nrf.send(buf)
                    # print(role,"message",msg[n],"sent")
                    flash_led(1)
                except OSError:
                    failed = true #this is just here so it's not an empty line
                    #print(role,"Sorry message not sent")
            nrf.send("\n")
        except:
            print(config["role"],"Sorry message not sent")       
        
        
        nrf.start_listening()
    nrf = setup()
    nrf.start_listening()
    msg_string = ""

import struct
import time
import json

from time import sleep

led = Pin(25, Pin.OUT) # Onboard LED
              
def flash_led(times:int=None):
    ''' Flashed the built in LED the number of times defined in the times parameter '''
    for _ in range(times):
        led.value(1)
        sleep(0.01)
        led.value(0)
        sleep(0.01)

# main code loop
flash_led(1)



while True:
    msg = ""
    if config["role"] == "send":
        if config["use_imu"]:
            data = {
                "ax":round(imu.accel.x,2),
                "ay":round(imu.accel.y,2),
                "az":round(imu.accel.z,2),
                "gx":round(imu.gyro.x),
                "gy":round(imu.gyro.y),
                "gz":round(imu.gyro.z),
                "tem":round(imu.temperature,2)
                }
        else:
            data = {"message":"hello there"}
        
        # print the keys and values
        for key in data:
            value = data[key]
            print("The key and value are ({}) = ({})".format(key, value))

        
        if config["use_oled"]:
            message = data
            showmessage(message)
        
        if config["use_nrf"]:
            send(nrf, json.dumps(data))
        
        time.sleep(0.8)
    else:
        if config["use_nrf"]:
            # Check for Messages
            if nrf.any():
                package = nrf.recv()          
                message = struct.unpack("s",package)
                msg = message[0].decode()
                flash_led(1)

                # Check for the new line character
                if (msg == "\n") and (len(msg_string) <= 20):
                    print("full message",msg_string, msg)
                    msg_string = ""
                else:
                    if len(msg_string) <= 20:
                        msg_string = msg_string + msg
                    else:
                        msg_string = ""






