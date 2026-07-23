package handlers

import (
    "net/http"
    "fmt"

    "backend/database"

    "github.com/gin-gonic/gin"
)

func GetTableAnalyst(c *gin.Context) {
    var signals []database.Signal
    
    if err := database.DB.Order("deposit DESC").Find(&signals).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    result := make([]gin.H, len(signals))
    for i, s := range signals {
        longSignal := "long_open"
        if s.LongSignal == "-1" {
            longSignal = "long_close"
        }
        shortSignal := "short_open"
        if s.ShortSignal == "1" {
            shortSignal = "short_close"
        }

        result[i] = gin.H{
            "id":            s.ID,
            "strategy":      s.Strategy,
            "long_signal":   longSignal,
            "short_signal":  shortSignal,
            "mode":          s.Mode,
            "status":        s.Status,
            "fiat":          fmt.Sprintf("%.2f", s.Fiat),
            "active":        fmt.Sprintf("%.2f", s.Active),
            "deposit":       fmt.Sprintf("%.2f", s.Deposit),
            "datetime":      s.Datetime.Format("2006-01-02 15:04"),
        }
    }

    c.JSON(http.StatusOK, result)
}

func GetTradesBySignal(c *gin.Context) {
    signalID := c.Param("signal_id")
    page := c.DefaultQuery("page", "1")
    limit := c.DefaultQuery("limit", "50")
    chartLimit := c.DefaultQuery("chart_limit", "50")

    // Парсинг параметров
    var pageInt, limitInt, chartLimitInt int
    fmt.Sscanf(page, "%d", &pageInt)
    fmt.Sscanf(limit, "%d", &limitInt)
    fmt.Sscanf(chartLimit, "%d", &chartLimitInt)

    if pageInt < 1 {
        pageInt = 1
    }
    if limitInt < 1 || limitInt > 500 {
        limitInt = 50
    }

    // Проверяем существование сигнала
    var signal database.Signal
    if err := database.DB.First(&signal, signalID).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "Signal not found"})
        return
    }

    // Общее количество трейдов
    var totalTrades int64
    database.DB.Model(&database.Trade{}).Where("signal_id = ?", signalID).Count(&totalTrades)

    // Трейды для графика
    var chartTrades []database.Trade
    query := database.DB.Where("signal_id = ?", signalID).Order("datetime DESC")
    if chartLimitInt != -1 {
        query = query.Limit(chartLimitInt)
    }
    query.Find(&chartTrades)
    
    // Разворачиваем для графика
    for i, j := 0, len(chartTrades)-1; i < j; i, j = i+1, j-1 {
        chartTrades[i], chartTrades[j] = chartTrades[j], chartTrades[i]
    }

    // Трейды для таблицы (с пагинацией)
    offset := (pageInt - 1) * limitInt
    var tableTrades []database.Trade
    database.DB.Where("signal_id = ?", signalID).
        Order("datetime DESC").
        Offset(offset).
        Limit(limitInt).
        Find(&tableTrades)

    // Формируем ответ
    chartData := make([]gin.H, len(chartTrades))
    for i, t := range chartTrades {
        datetime := "N/A"
        if !t.Datetime.IsZero() {
            datetime = t.Datetime.Format("2006-01-02 15:04")
        }
        chartData[i] = gin.H{
            "id":       t.ID,
            "deposit":  fmt.Sprintf("%.2f", t.Deposit),
            "datetime": datetime,
        }
    }

    tableData := make([]gin.H, len(tableTrades))
    for i, t := range tableTrades {
        datetime := "N/A"
        if !t.Datetime.IsZero() {
            datetime = t.Datetime.Format("2006-01-02 15:04")
        }
        tableData[i] = gin.H{
            "id":       t.ID,
            "deposit":  fmt.Sprintf("%.2f", t.Deposit),
            "datetime": datetime,
        }
    }

    totalPages := int((totalTrades + int64(limitInt) - 1) / int64(limitInt))
    if totalPages < 1 {
        totalPages = 1
    }

    c.JSON(http.StatusOK, gin.H{
        "strategy": signal.Strategy,
        "chart_data": chartData,
        "table_data": tableData,
        "pagination": gin.H{
            "current_page": pageInt,
            "limit": limitInt,
            "total": totalTrades,
            "total_pages": totalPages,
        },
        "statistics": gin.H{
            "total_trades": totalTrades,
        },
    })
}