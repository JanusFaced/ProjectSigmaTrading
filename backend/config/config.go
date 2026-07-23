package config

import (
    "log"
    "os"

    "github.com/joho/godotenv"
)

type Config struct {
    DBHost     string
    DBPort     string
    DBUser     string
    DBPassword string
    DBName     string
    AdminKey   string
    ModeWork   string
}

func LoadConfig() *Config {
    err := godotenv.Load()
    if err != nil {
        log.Println("No .env file found, using system env")
    }

    return &Config{
        DBHost:     getEnv("DB_HOST", "localhost"),
        DBPort:     getEnv("DB_PORT", "5432"),
        DBUser:     getEnv("DB_USER", "postgres"),
        DBPassword: getEnv("DB_PASSWORD", ""),
        DBName:     getEnv("DB_NAME", "postgres"),
        AdminKey:   getEnv("ADMIN_KEY", "admin123"),
        ModeWork:   getEnv("MODE_WORK", "localhost"),
    }
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}