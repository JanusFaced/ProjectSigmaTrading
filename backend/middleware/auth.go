package middleware

import (
    "net/http"
    "os"

    "github.com/gin-gonic/gin"
)

func AdminAuth() gin.HandlerFunc {
    return func(c *gin.Context) {
        apiKey := c.GetHeader("X-API-Key")
        adminKey := os.Getenv("ADMIN_KEY")
        
        if apiKey == "" || apiKey != adminKey {
            c.JSON(http.StatusForbidden, gin.H{"error": "Invalid admin API key"})
            c.Abort()
            return
        }
        c.Next()
    }
}