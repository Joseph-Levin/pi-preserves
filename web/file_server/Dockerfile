FROM alpine as build-env
RUN apk add --no-cache build-base
WORKDIR /file_server
COPY . .
RUN gcc -Wall -pedantic -o server server.c

FROM alpine
COPY --from=build-env /file_server/server /file_server/server
WORKDIR /file_server
CMD ["/file_server/server"]