FROM golang:1.22-alpine AS builder
RUN apk add --no-cache git ca-certificates
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /app/main \
    .

FROM alpine:3.18
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/main /usr/local/bin/app
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/app"]