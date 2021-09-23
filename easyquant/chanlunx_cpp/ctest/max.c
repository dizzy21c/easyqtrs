

#include "stdio.h"
void display(char* msg){
    printf("%s\n",msg);
}
  
int add(int a,int b){
    return a+b;
}

float* calcf(float* f)
{
  f[0] = 1.0;
  return f;
}

void calc2(int l, float* fo, float* fi) 
{
  for(int i = 0; i < l; i++)
  {
    fo[i] = 2 * fi[i];
  }
}
int max(int a, int b)
{
  return a>b?a:b;
}

