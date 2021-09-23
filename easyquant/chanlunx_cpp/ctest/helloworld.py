import ctypes

libc = ctypes.cdll.LoadLibrary("./hello_module.so")

libc.main()
libc.main2()