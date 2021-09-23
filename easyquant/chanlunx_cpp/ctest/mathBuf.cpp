#include <iostream>
#include "subBuf.h"

extern "C" 
{
    int addBuf(char* data, int num, char* outData);

    subBuf* subBuf_new(){ return new subBuf(); }
    int subBuf_sub(subBuf* subfuf, char* data, int num, char* outData){ subfuf->cursubBuf(data, num, outData); }
}

int addBuf(char* data, int num, char* outData)
{
    for (int i = 0; i < num; ++i)
    {
        outData[i] = data[i] + 3;
    }
    return num;
}
