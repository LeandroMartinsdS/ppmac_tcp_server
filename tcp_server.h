/*
 * =============================================================================
 * File        : tcp_server.h
 * Author      : Leandro Martins dos Santos
 * Description : Functions and constants declarations for TCP server.
 * =============================================================================
 */

#ifndef TCP_SERVER_H
#define TCP_SERVER_H

#define SIMULATION_MODE   // Comment out if executing on the Power PMAC
#ifndef SIMULATION_MODE
// #define RUN_AS_RT_APP
// #define DEBUG
#endif // SIMULATION_MODE

// Socket settings
#define MAXPENDING 5
#define VAR_NUM     7
#define BUFFSIZE VAR_NUM*sizeof(double)
#define SHUTDOWN_CMD "SHUTDOWN"

// Constants
#ifdef SIMULATION_MODE
    # define MAX_P 65536
    struct SHM {
        double P[MAX_P];            // Global P variable Array
    };
    struct SHM  *pshm;              // Pointer to shared memory
    void        *pushm;             // Pointer to user shared memory

    #include <stdio.h>
    #include <stdlib.h>
    // #include <stdbool.h>
    #include <string.h>
    #include <stddef.h>
    //
    #include <sys/types.h>
    #include <asm-generic/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <signal.h>
    #include <unistd.h>

    #define MASTER_ECT_BASE 0

#else
    #include <gplib.h>
    #include <stdlib.h>
    #include <errno.h>

    #define _PPScriptMode_		// for enum mode, replace this with #define _EnumMode_
    #include "../../Include/pp_proj.h"

    #define MASTER_ECT_BASE 19
#endif // SIMULATION_MODE

int serverSock;

void InitSocket(char *host, int port);
int AcceptClient(void);
int HandleClient(int clientSock, char *buffer, size_t data_size);
// TO DO: create status type for socket
void CloseSocket(int sock);
void Die(char *message);
void kill_handler(int sig);
void test_process_data(double *dest, double *src, size_t data_size);

#endif // TCP_SERVER_H