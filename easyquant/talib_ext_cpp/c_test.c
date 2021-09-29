#include <stdio.h>
#include <stdlib.h>
#include <math.h>

void test(int *p, float *f) {
  *p += 2;
  f[0] = 12.0;
  f[1] = 22.0;
  f[3] = 32.0;
}

typedef struct DictSt {
    int key;
    float value;
} Dict;

int test2(void) {
    int *pa = malloc(10 * sizeof(int)); // allocate an array of 10 int
    if(pa) {
        printf("%zu bytes allocated. Storing ints: ", 10*sizeof(int));
        for(int n = 0; n < 10; ++n)
            printf("%d ", pa[n] = n);
    }

    int *pb = realloc(pa, 1000000 * sizeof(int)); // reallocate array to a larger size
    if(pb) {
        printf("\n%zu bytes allocated, first 10 ints are: ", 1000000*sizeof(int));
        for(int n = 0; n < 10; ++n)
        printf("%d ", pb[n]); // show the array
        free(pb);
    } else { // if realloc failed, the original pointer needs to be freed
        free(pa);
    }
}

void test3(Dict *dpTest) {
    Dict t1 = {10, 13.0};
//    t.key = 12.9;
//    t.value = 13.0;
    dpTest[0] = (Dict) {10, 13.0};
    dpTest[1] = (Dict) {5, 13.0};
    dpTest[2] = (Dict) {7, 13.0};
}

int compare_function(const void *a,const void *b) {
    Dict *x = (Dict *) a;
    Dict *y = (Dict *) b;
    return x->key - y->key;
}


int main()
{
   /* 我的第一个 C 程序 */
   printf("Hello, World! \n");
   float fv = 123.34;
   float f2i = floor(fv);
   printf("Hello, World! %d, %f \n", int(f2i), f2i);

    float tf1 = 7.44f;
    float tf2 = 7.09f;
    float minD = 0.01f;
    int ch1 = floor((tf1 - tf2) / minD);
    int ch2 = floor((tf1*100 - tf2*100) / 100 / minD);
   printf("Hello, World! %d, %f \n", ch2, (tf1 - tf2) / minD);

   int p = 0;
//   float *f = (float*)malloc(sizeof(float) * 10);
   float *f = (float*)malloc(sizeof(float) * 1);
   test(&p, f);
   printf("Hello, World! %d, %f \n", p, f[2]);
   test(&p, f);
   printf("Hello, World! %d, %f \n", p, f[2]);
   test(&p, f);
   printf("Hello, World! %d, %f \n", p, f[2]);

   free(f);

   test2();

    Dict *dpTest = (Dict*) malloc(sizeof(Dict) * 3);
    test3(dpTest);
    printf("Hello, World! %d, %f \n", p, dpTest[0].key);
    for(int i = 0; i < 3; i++) {
        printf("key %d", dpTest[i]);
    }
    qsort(dpTest, 3, sizeof(Dict), compare_function);
    for(int i = 0; i < 3; i++) {
        printf("key %d", dpTest[i]);
    }

   return 0;
}
