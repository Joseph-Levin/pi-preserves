#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

#define SIZE 2048
#define FAILURE "/--FAILURE--/"


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


void write_file(int sockfd) {
    int n;
    FILE* fp;
    char filename[SIZE] = {0};
    char buffer[SIZE+1];

    n = recv(sockfd, filename, SIZE, 0);
    printf("Received filename: %s\n", filename);

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


int main()
{
    char *ip = "127.0.0.1";
    int port = 8888;
    int e;

    int sockfd, new_sock;
    struct sockaddr_in server_addr, new_addr;
    socklen_t addr_size;

    // Initialize socket and check for errors
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("Error in socket init\n");
        exit(1);
    }

    printf("Server socket created.\n");

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(ip);

    e = bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr));
    if (e < 0)
    {
        perror("Error in binding\n");
        exit(1);
    }

    printf("Binding successful\n");

    e = listen(sockfd, 10);
    if (e == 0)
    {
        printf("listening...\n");
        while (1) {
            addr_size = sizeof(new_addr);
            new_sock = accept(sockfd, (struct sockaddr *)&new_addr, &addr_size);
            if (new_sock < 0){
                printf("Error in accepting a connection\n");
                continue;
            }

            printf("Accepted connection from %s\n", inet_ntoa(new_addr.sin_addr));

            // Receive type of request from connection
            char request[16];
            recv(new_sock, request, 16, 0);
            send_ack(new_sock);

            if (strncmp(request, "upload", 6) == 0){
                write_file(new_sock);
            }
            else if(strncmp(request, "download", 8) == 0){
                send_file(new_sock);
            }
            else {
                printf("Unknown request\n");
            }

            // Close new socket
            shutdown(new_sock,SHUT_RDWR);
            printf("Completed shutdown\n");

        }

    }
    else
    {
        perror("Error in listening");
        exit(1);
    }

}
