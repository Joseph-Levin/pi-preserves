#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define SIZE 1024

void send_file(FILE* fp, int sockfd) {
  char data[SIZE] = {0};
  
  while(fgets(data, sizeof(data), fp) != NULL) {
    if (send(sockfd, data, sizeof(data), 0) == -1) {
      perror("Error in sending data");
      exit(1);
    }
    bzero(data, SIZE);
  }
}

int main(int argc, char** argv)
{
  char *ip = "127.0.0.1";
  int port = 8888;
  int e;

  int sockfd;
  struct sockaddr_in server_addr;
  FILE* fp;
  char* filename = argv[1];

  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {
    perror("Error in socket");
    exit(1);
  }
  printf("Socket created\n");

  server_addr.sin_family = AF_INET;
  server_addr.sin_port = port;
  server_addr.sin_addr.s_addr = inet_addr(ip);

  e = connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));
  if (e == -1) {
    perror("Error in connecting");
    exit(1);
  }
  printf("Connected to server\n");

  fp = fopen(filename, "r");
  if (fp == NULL) {
    perror("Error in reading file");
    exit(1);
  }

  send_file(fp, sockfd);
  printf("File sent successfully\n");

  close(sockfd);
  printf("Disconneced from server\n");


}