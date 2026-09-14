package handlers

import (
    "net/http"
    "fmt"

    "backend/database"

    "github.com/gin-gonic/gin"
)

/*
func GetPortfolio(c *gin.Context) {
    var portfolios []database.CurrentPortfolio
    
    if err := database.DB.Order("full_profit DESC").Find(&portfolios).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    result := make([]gin.H, len(portfolios))
    for i, s := range portfolios {

        result[i] = gin.H{
            "id":             s.ID,
            "name_portfolio": s.NamePortfolio,
            "portfolio":      fmt.Sprintf("%.2f", s.Portfolio),
            "full_profit":    fmt.Sprintf("%.2f", s.FullProfit),
            "year_profit":    fmt.Sprintf("%.2f", s.YearProfit),
            "max_drawdown":   fmt.Sprintf("%.2f", s.MaxDrawdown),
            "sharp":          fmt.Sprintf("%.2f", s.Sharp),
            "profit_factor":  fmt.Sprintf("%.2f", s.ProfitFactor),
            "datetime":       s.Datetime.Format("2006-01-02 15:04"),
        }
    }

    c.JSON(http.StatusOK, result)
}
*/

func GetPortfolio(c *gin.Context) {
    var portfolio database.CurrentPortfolio

    if err := database.DB.Order("full_profit DESC").First(&portfolio).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "Portfolio not found"})
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "id":             portfolio.ID,
        "name_portfolio": portfolio.NamePortfolio,
        "portfolio":      fmt.Sprintf("%.2f", portfolio.Portfolio),
        "full_profit":    fmt.Sprintf("%.2f", portfolio.FullProfit),
        "year_profit":    fmt.Sprintf("%.2f", portfolio.YearProfit),
        "max_drawdown":   fmt.Sprintf("%.2f", portfolio.MaxDrawdown),
        "sharp":          fmt.Sprintf("%.2f", portfolio.Sharp),
        "profit_factor":  fmt.Sprintf("%.2f", portfolio.ProfitFactor),
        "datetime":       portfolio.Datetime.Format("2006-01-02 15:04"),
    })
}


func GetHistoryPortfolio(c *gin.Context) {
    CurrentPortfolioID := c.Param("current_portfolio_id")

    page := c.DefaultQuery("page", "1")
    limit := c.DefaultQuery("limit", "50")
    chartLimit := c.DefaultQuery("chart_limit", "50")

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

    var currentPortfolio database.CurrentPortfolio
    if err := database.DB.First(&currentPortfolio, CurrentPortfolioID).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "CurrentPortfolio not found"})
        return
    }

    var totalDays int64
    database.DB.Model(&database.HistoryPortfolio{}).Where("current_portfolio_id = ?", CurrentPortfolioID).Count(&totalDays)

    var chartDays []database.HistoryPortfolio
    query := database.DB.Where("current_portfolio_id = ?", CurrentPortfolioID).Order("datetime DESC")
    if chartLimitInt != -1 {
        query = query.Limit(chartLimitInt)
    }
    query.Find(&chartDays)
    
    for i, j := 0, len(chartDays)-1; i < j; i, j = i+1, j-1 {
        chartDays[i], chartDays[j] = chartDays[j], chartDays[i]
    }

    offset := (pageInt - 1) * limitInt
    var tableDays []database.HistoryPortfolio
    database.DB.Where("current_portfolio_id = ?", CurrentPortfolioID).
        Order("datetime DESC").
        Offset(offset).
        Limit(limitInt).
        Find(&tableDays)

    chartData := make([]gin.H, len(chartDays))
    for i, t := range chartDays {
        datetime := "N/A"
        if !t.Datetime.IsZero() {
            datetime = t.Datetime.Format("2006-01-02 15:04")
        }
        chartData[i] = gin.H{
            "id":        t.ID,
            "portfolio": fmt.Sprintf("%.2f", t.Portfolio),
            "datetime":  datetime,
        }
    }

    tableData := make([]gin.H, len(tableDays))
    for i, t := range tableDays {
        datetime := "N/A"
        if !t.Datetime.IsZero() {
            datetime = t.Datetime.Format("2006-01-02 15:04")
        }
        tableData[i] = gin.H{
            "id":        t.ID,
            "portfolio": fmt.Sprintf("%.2f", t.Portfolio),
            "datetime":  datetime,
        }
    }

    totalPages := int((totalDays + int64(limitInt) - 1) / int64(limitInt))
    if totalPages < 1 {
        totalPages = 1
    }

    c.JSON(http.StatusOK, gin.H{
        "strategy": currentPortfolio.NamePortfolio,
        "chart_data": chartData,
        "table_data": tableData,
        "pagination": gin.H{
            "current_page": pageInt,
            "limit": limitInt,
            "total": totalDays,
            "total_pages": totalPages,
        },
        "statistics": gin.H{
            "total_days": totalDays,
        },
    })
}

