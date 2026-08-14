#include <stdio.h>
#include <stdlib.h>

int fibonacci_calculator(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main(int argc, char *argv[]) {
    int n;
    if (argc > 1) {
        n = (int)atoi(argv[1]);
    } else {
        n = 0;
    }
    int result = fibonacci_calculator(n);
    printf("%d\n", result);
    return 0;
}
