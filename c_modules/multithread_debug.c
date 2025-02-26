#include <windows.h>
#include <stdio.h>

DWORD WINAPI thread_function(LPVOID lpParam) {
    int id = *(int*)lpParam;
    int counter = 0;
    
    while(1) {
        counter++;  // Set breakpoint here
        printf("Thread %d: counter = %d\n", id, counter);
        Sleep(1000);
    }
    return 0;
}

int main() {
    int id1 = 1, id2 = 2;
    HANDLE threads[2];
    
    threads[0] = CreateThread(NULL, 0, thread_function, &id1, 0, NULL);
    threads[1] = CreateThread(NULL, 0, thread_function, &id2, 0, NULL);
    
    WaitForMultipleObjects(2, threads, TRUE, INFINITE);
    return 0;
}