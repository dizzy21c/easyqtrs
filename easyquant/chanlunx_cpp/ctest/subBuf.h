#include <iostream>

class subBuf{
    public:
        subBuf(){}
        int cursubBuf(char* data, int num, char* outData)
        {
            for (int i = 0; i < num; ++i)
            {
                outData[i] = data[i] - 5;
            }
            return num;
        }
};