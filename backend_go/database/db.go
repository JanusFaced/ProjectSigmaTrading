package database

import (
    "fmt"
    "log"
    "time"

    "backend/config"

    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

var DB *gorm.DB

func InitDB(cfg *config.Config) {
    dsn := fmt.Sprintf(
        "host=%s user=%s password=%s dbname=%s port=%s sslmode=disable TimeZone=UTC",
        cfg.DBHost, cfg.DBUser, cfg.DBPassword, cfg.DBName, cfg.DBPort,
    )

    var err error
    DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Info),
        NowFunc: func() time.Time {
            return time.Now().UTC()
        },
    })
    if err != nil {
        log.Fatal("Failed to connect to database:", err)
    }

    sqlDB, err := DB.DB()
    if err != nil {
        log.Fatal("Failed to get database instance:", err)
    }

    sqlDB.SetMaxIdleConns(10)
    sqlDB.SetMaxOpenConns(20)
    sqlDB.SetConnMaxLifetime(time.Hour)

    // Автоматическая миграция
    err = DB.AutoMigrate(&Backtest{}, &Signal{}, &Trade{})
    if err != nil {
        log.Fatal("Failed to migrate database:", err)
    }

    log.Println("Database connected and migrated")
}

func GetDB() *gorm.DB {
    return DB
}