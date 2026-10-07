import machine
import neopixel
import sys
import select

led =  neopixel.NeoPixel(machine.Pin(4),2)

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

def read(n):
    buf = b""
    while len(buf) < n:
        if poller.poll(1000):
            chunk = sys.stdin.buffer.read(n - len(buf))
            if chunk:
                buf += chunk
        else:
            return None
    return buf

while 1:
    b1 = read(1)
    if b1 is None or b1[0] != 0xAA:
        continue
    b2 = read(1)
    if b2 is None or b2[0] != 0x55:
        continue

    payload = read(96*3)
    if payload is None:
        continue
    chk = read(1)
    if chk is None:
        continue
    for i in range(96):
        o = i*3
        led[i] = (payload[o], payload[o + 1], payload[o + 2])
    led.write()