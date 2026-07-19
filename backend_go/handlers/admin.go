package handlers

import (
    "net/http"
    "fmt"

    "backend/database"

    "github.com/gin-gonic/gin"
)

func DeleteSignal(c *gin.Context) {
    signalID := c.Param("signal_id")

    // Проверяем существование сигнала
    var signal database.Signal
    if err := database.DB.First(&signal, signalID).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "Signal not found"})
        return
    }

    signalName := signal.Strategy
    var tradesCount int64
    database.DB.Model(&database.Trade{}).Where("signal_id = ?", signalID).Count(&tradesCount)

    // Удаляем трейды и сигнал (каскадное удаление)
    if err := database.DB.Delete(&signal).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Error deleting signal: %v", err)})
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "success": true,
        "message": fmt.Sprintf("Сигнал '%s' успешно удален", signalName),
        "deleted_signal_id": signalID,
        "deleted_trades_count": tradesCount,
        "signal_name": signalName,
    })
}

func GetAdminStatistics(c *gin.Context) {
    var signalsCount, backtestsCount, tradesCount int64
    database.DB.Model(&database.Signal{}).Count(&signalsCount)
    database.DB.Model(&database.Backtest{}).Count(&backtestsCount)
    database.DB.Model(&database.Trade{}).Count(&tradesCount)

    var signals []database.Signal
    database.DB.Find(&signals)

    signalsList := make([]gin.H, len(signals))
    for i, s := range signals {
        var trades int64
        database.DB.Model(&database.Trade{}).Where("signal_id = ?", s.ID).Count(&trades)
        
        datetime := "N/A"
        if !s.Datetime.IsZero() {
            datetime = s.Datetime.Format("2006-01-02 15:04")
        }

        signalsList[i] = gin.H{
            "id":           s.ID,
            "strategy":     s.Strategy,
            "deposit":      s.Deposit,
            "status":       s.Status,
            "trades_count": trades,
            "datetime":     datetime,
        }
    }

    c.JSON(http.StatusOK, gin.H{
        "total_signals":   signalsCount,
        "total_backtests": backtestsCount,
        "total_trades":    tradesCount,
        "signals":         signalsList,
    })
}