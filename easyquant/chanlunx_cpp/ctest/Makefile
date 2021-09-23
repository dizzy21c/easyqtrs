####
gcc -Wall -g  -fPIC -c max.c -o max.o
gcc -shared max.o -o max.so
#-g -Wall 供调试使用，不是必须的<br> * 或者<br> * gcc max.c -fPIC -shared -o max.so

gcc -shared -Wl,-soname,hello_module -o hello_module.so -fPIC helloworld.cpp
g++ -shared -Wl,-soname,hello_module -o hello_module.so -fPIC helloworld.cpp
