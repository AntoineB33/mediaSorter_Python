#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

// 1. Erreur de dépassement de tableau (stack)
void stack_buffer_overflow() {
    int stack_array[5] = {1, 2, 3, 4, 5};
    for(int i = 0; i <= 5; i++) {  // Erreur délibérée : i <= 5 au lieu de i < 5
        printf("Stack[%d] = %d\n", i, stack_array[i]);
    }
}

// 2. Erreur de dépassement de tableau (heap)
void heap_buffer_overflow() {
    int* heap_array = malloc(3 * sizeof(int));
    for(int i = 0; i < 4; i++) {  // Erreur délibérée : écriture au-delà du malloc(3)
        heap_array[i] = i * 10;
    }
    free(heap_array);
}

// 3. Accès à une adresse libérée
void use_after_free() {
    int* ptr = malloc(sizeof(int));
    *ptr = 42;
    free(ptr);
    printf("Valeur après free: %d\n", *ptr);  // Erreur délibérée
}

int main() {
    printf("=== Début du test ===\n");
    
    // stack_buffer_overflow();  // Décommenter pour tester
    heap_buffer_overflow();   // Décommenter pour tester
    // use_after_free();         // Décommenter pour tester
    
    printf("=== Fin du test ===\n");
    return 0;
}