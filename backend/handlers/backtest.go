package handlers

import (
    "net/http"

    "backend/database"

    "github.com/gin-gonic/gin"
)

func GetTableBacktest(c *gin.Context) {
    var backtests []database.Backtest
    
    if err := database.DB.Order("year_profit DESC").Find(&backtests).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    result := make([]gin.H, len(backtests))
    for i, b := range backtests {
        result[i] = gin.H{
            "id":           b.ID,
            "strategy":     b.Strategy,
            "year_profit":  b.YearProfit,
            "max_drawdown": b.MaxDrawdown,
            "sharp":        b.Sharp,
            "datetime":     b.Datetime,
        }
    }

    c.JSON(http.StatusOK, result)
}