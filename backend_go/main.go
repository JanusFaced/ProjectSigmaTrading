package main

import (
    "log"
    "net/http"

    "backend/config"
    "backend/database"
    "backend/handlers"
    "backend/middleware"

    "github.com/gin-contrib/cors"
    "github.com/gin-gonic/gin"
)

func main() {
    // Загружаем конфиг
    cfg := config.LoadConfig()

    // Подключаем базу данных
    database.InitDB(cfg)

    // Создаем роутер
    router := gin.Default()

    // Настройка CORS
    corsConfig := cors.DefaultConfig()
    if cfg.ModeWork == "localhost" {
        corsConfig.AllowAllOrigins = true
    } else {
        corsConfig.AllowOrigins = []string{
            "https://projectsigmatrading.ru",
            "http://projectsigmatrading.ru",
            "https://62.113.37.47",
            "http://62.113.37.47",
        }
    }
    corsConfig.AllowCredentials = true
    corsConfig.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
    corsConfig.AllowHeaders = []string{"Origin", "Content-Length", "Content-Type", "X-API-Key"}
    router.Use(cors.New(corsConfig))

    // Публичные эндпоинты
    router.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "healthy", "framework": "Go/Gin"})
    })

    router.GET("/", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "message": "Signals API",
            "version": "1.0.0",
            "endpoints": []string{
                "/getTableBacktest",
                "/getTableAnalyst",
                "/getTradesBySignal/:signal_id",
                "/admin/delete-signal/:signal_id",
                "/admin/statistics",
                "/health",
            },
        })
    })

    // Основные эндпоинты
    router.GET("/getTableBacktest", handlers.GetTableBacktest)
    router.GET("/getTableAnalyst", handlers.GetTableAnalyst)
    router.GET("/getTradesBySignal/:signal_id", handlers.GetTradesBySignal)

    // Админские эндпоинты (с защитой)
    admin := router.Group("/admin")
    admin.Use(middleware.AdminAuth())
    {
        admin.DELETE("/delete-signal/:signal_id", handlers.DeleteSignal)
        admin.GET("/statistics", handlers.GetAdminStatistics)
    }

    // Запускаем сервер
    log.Println("Server starting on :8000")
    if err := router.Run(":8000"); err != nil {
        log.Fatal("Failed to start server:", err)
    }
}