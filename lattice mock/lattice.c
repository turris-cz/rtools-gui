#include <stdio.h>
#include <string.h>
#include <unistd.h>


int main(int argc, char* argv[]) {
    int i;
    char logfile[100] = "";
    
    for (i=0; i<argc; i++) {
        if (strcmp(argv[i], "-logfile") == 0 &&
                (i + 1 < argc)) {
            strcpy(logfile, argv[i+1]);
            break;
        }
    }
    
    if (!strlen(logfile)) {
        printf("missing logfile\n");
        return 1;
    }
    
    sleep(10);
    FILE* f = fopen(logfile, "w");
    fprintf(f, "         Lattice Semiconductor Corporation.\n"
"            Lattice Diamond Programmer 2.0 Command Line\n"
"\n"
"\n"
"\n"
"System Information:\n"
"-----------------------------------------------------\n"
"Linux turrisprogrammer01 3.8.0-19-generic #29-Ubuntu SMP Wed Apr 17 18:16:28 UTC 2013 x86_64 x86_64 x86_64 GNU/Linux\n"
"USB V2.0 detected.\n"
"\n"
"Check configuration setup: Start.\n"
"JTAG Chain Verification. No Errors.\n"
"Check configuration setup: Successful.\n"
"Device1 LCMXO1200C: FLASH Erase,Program,Verify\n"
"\n"
"Number of Loop = 13/100\n"
"Execution time: 00 min : 05 sec\n"
"Operation Done. No errors.\n"
"Elapsed time: 00 min : 05 sec\n"
"Operation: successful.\n"
    );
    fclose(f);
    printf("naflashovane uspesne\n");
    
    // cause the segfault
    int* segfault = 3000;
    *segfault = 20;
    
    return 0;
}
