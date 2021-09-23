from ctypes import * # cdll, c_int
lib = cdll.LoadLibrary('./libmathBuf.so')

class callsubBuf(object):
    def __init__(self):
        self.obj = lib.subBuf_new()

    def callcursubBuf(self, data, num, outData):
        lib.subBuf_sub(self.obj, data, num, outData)

callAddBuf = lib.addBuf

num = 4
numbytes = c_int(num)

data_in = (c_byte * num)()
for i in range(num):
    data_in[i] = i

print("initial input data buf:")
for i in range(num):
    print(data_in[i])

#pdata_in = cast(data_in, POINTER(c_ubyte))
#pdata_in2 = cast(pdata_in, POINTER(c_ubyte*num))

data_out = (c_byte * num)()

ret = callAddBuf(data_in, numbytes, data_out)

print("after call addBuf with C, output buf:")
for i in range(num):
    print(data_out[i])

f = callsubBuf()
f.callcursubBuf(data_in, numbytes, data_out)

print("after call cursubBuf with  C++ class, output buf:")
for i in range(num):
    print(data_out[i])