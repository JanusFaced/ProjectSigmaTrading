FROM rust:1.91-slim-bullseye AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY Cargo.toml Cargo.lock* ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
COPY src/ ./src/
RUN touch src/main.rs && cargo build --release

FROM debian:bullseye-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/parser /app/parser
RUN chmod +x /app/parser
EXPOSE 8080
CMD ["/app/parser"]