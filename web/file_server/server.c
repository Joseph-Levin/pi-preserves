#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <errno.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/time.h>
#include <sys/stat.h>

#define SIZE 2048
#define FAILURE "/--FAILURE--/"
#define MAX_CLIENTS 100
#define FILE_DEPTH 4


void send_ack(int sockfd) {
    char ack[4] = "ACK";

    send(sockfd, ack, 4, 0);
    return;
}


int recv_ack(int sockfd) {
    char ack[4] = "ACK";
    char buf[4] = {0};

    recv(sockfd, buf, 4, 0);

    if (strncmp(buf, ack, 4) != 0){
       printf("ACK not received\n");
       return 0; 
    }

    return 1;
}

void split_path_file(char* filename) {
    int i=0;
    DIR* dir;
    char sep[] = "/";
    char path[SIZE] = {0};
    strcpy(path, filename);
    char* ptr = strtok(path, sep);
    char* prev = NULL;
    char* appended_path = calloc(2048, sizeof(char));

    while(ptr != NULL){
        if (prev) {
            printf("%s\n", prev);
            char* token = calloc(256, sizeof(char));
            strcpy(token, prev);
            strcat(appended_path, token);
            strcat(appended_path, sep);
            printf("appended %s\n", appended_path);
            dir = opendir(appended_path);
            // if dir doesn't exist, create it
            if (!dir){
               mkdir(appended_path, 0777);
            }
            free(token);
        }

        prev = ptr;
        ptr = strtok(NULL, "/");
        i++;
    }
    free(appended_path);
    printf("in split: %s\n", filename);
}


void write_file(int sockfd) {
    int n;
    FILE* fp;
    char filename[SIZE] = {0};
    char buffer[SIZE+1];

    n = recv(sockfd, filename, SIZE, 0);
    printf("Received filename: %s\n", filename);

    split_path_file(filename);
    printf("filename: %s\n", filename);
    fp = fopen(filename, "wb");
    if (fp == NULL) {
        perror("Error in creating file");
        send(sockfd, FAILURE, 14, 0);
        return;
    }

    send_ack(sockfd);
    while(1) {
        memset(buffer, 0, SIZE);
        n = recv(sockfd, buffer, SIZE, 0);
        send_ack(sockfd);
        if (n <= 0) {
            break;
        }
        // fprintf(fp, "%s", buffer);
        fwrite(buffer, 1, n, fp);
    }
    fclose(fp);
    return;

}


void send_file(int sockfd) {
    int n;
    FILE* fp;
    char filename[SIZE] = {0};
    char buffer[SIZE] = {0};

    memset(filename, 0, SIZE);
    recv(sockfd, filename, SIZE, 0);
    printf("Received filename: %s\n", filename);

    fp = fopen(filename, "r");
    if (fp == NULL) {
        perror("Error in opening file");
        send(sockfd, FAILURE, 14, 0);
        return;
    }

    send_ack(sockfd);
    while((n=fread(buffer, 1, SIZE, fp)) > 0) {
        send(sockfd, buffer, n, 0);
        memset(buffer, 0, SIZE);
        recv_ack(sockfd);
    }
    fclose(fp);
    return;

}


void delete_file(int sockfd) {
    char filename[SIZE] = {0};
    recv(sockfd, filename, SIZE, 0);
    send_ack(sockfd);
    printf("Deleting: %s\n", filename);
    // Successfully removed the file
    if (remove(filename) == 0) {
        send_ack(sockfd);
    }
    else {
        perror("Error in deleting file");
        send(sockfd, FAILURE, 14, 0);
    }
    return;
}

void get_size(int sockfd){
    FILE* fp;
    char filename[SIZE] = {0};

    memset(filename, 0, SIZE);
    recv(sockfd, filename, SIZE, 0);
    printf("Received filename: %s\n", filename);

    fp = fopen(filename, "r");
    if (fp == NULL) {
        perror("Error in opening file");
        send(sockfd, FAILURE, 14, 0);
        return;
    }

    send_ack(sockfd);

    fseek(fp, 0, SEEK_END);
    int size = ftell(fp);
    fclose(fp);
    printf("Size of %s is %d\n", filename, size);
    uint32_t x = htonl(size);

    send(sockfd, &x, sizeof(uint32_t), 0);
    recv_ack(sockfd);
    return;
}


int main()
{
    char *ip = "127.0.0.1";
    int port = 8888;
    int e;

    int main_sock, new_sock, max_sock;
    int i;
    int activity;
    int clients[MAX_CLIENTS] = {-1};

    struct sockaddr_in server_addr, new_addr;
    socklen_t addr_size;
    int opt = 1; // TRUE value
    fd_set readfds;

    // Initialize socket and check for errors
    main_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (main_sock < 0)
    {
        perror("Error in socket init\n");
        exit(1);
    }

    if (setsockopt(main_sock, SOL_SOCKET, SO_REUSEADDR, (char*)&opt, sizeof(opt)) < 0) {
        perror("setsockopt failure");
        exit(1);
    }
    printf("Server socket created.\n");

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(ip);

    e = bind(main_sock, (struct sockaddr *)&server_addr, sizeof(server_addr));
    if (e < 0)
    {
        perror("Error in binding\n");
        exit(1);
    }

    printf("Binding successful\n");

    if (listen(main_sock, 10) < 0) {
        perror("Error in listening");
        exit(1);
    }

    printf("listening...\n");
    addr_size = sizeof(new_addr);

    while (1) {
        FD_ZERO(&readfds);
        FD_SET(main_sock, &readfds);
        max_sock = main_sock;

        for (i=0; i < MAX_CLIENTS; i++) {
            if (clients[i] > 0) {
                FD_SET(clients[i], &readfds);
            }

            if (clients[i] > max_sock) {
                max_sock = clients[i];
            }
        }

        activity = select(max_sock+1, &readfds, NULL, NULL, NULL);
        if (activity < 0 && errno != EINTR) {
            perror("Select error");
            exit(1);
        }
        
        // New connection coming from main server socket
        if (FD_ISSET(main_sock, &readfds)) {
            if ((new_sock = accept(main_sock, (struct sockaddr *)&new_addr, &addr_size)) < 0) {
                perror("Accept error");
                exit(1);
            }

            printf("Accepted connection from %s:%hu. Assigned to socket: %d\n", inet_ntoa(new_addr.sin_addr), ntohs(new_addr.sin_port), new_sock);

            // Add to active clients
            for (i=0; i < MAX_CLIENTS; i++) {
                if (clients[i] == -1) {
                    clients[i] = new_sock;
                    break;
                }
            }
        }
        // Activity on another socket
        else {
            for (i=0; i < MAX_CLIENTS; i++) {
                if (FD_ISSET(clients[i], &readfds)) {
                    // Receive type of request from connection
                    char request[16];
                    recv(clients[i], request, 16, 0);
                    send_ack(clients[i]);

                    if (strncmp(request, "upload", 6) == 0){
                        write_file(clients[i]);
                    }
                    else if(strncmp(request, "download", 8) == 0){
                        send_file(clients[i]);
                    }
                    else if (strncmp(request, "delete", 6) == 0) {
                        delete_file(clients[i]);
                    }
                    else if (strncmp(request, "size", 4) == 0) {
                        get_size(clients[i]);
                    }
                    else {
                        printf("Unknown request\n");
                    }

                    // Close new socket
                    close(clients[i]);
                    clients[i] = -1;
                    printf("Completed shutdown\n");

                }
            }

        }
        if (new_sock < 0){
            printf("Error in accepting a connection\n");
            continue;
        }



    }


}
