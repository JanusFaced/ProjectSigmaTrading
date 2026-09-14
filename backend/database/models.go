package database

import (
    "time"
)

type Backtest struct {
    ID          uint      `gorm:"primaryKey" json:"id"`
    Strategy    string    `gorm:"size:100;uniqueIndex;not null" json:"strategy"`
    YearProfit  float64   `gorm:"not null" json:"year_profit"`
    MaxDrawdown float64   `gorm:"not null" json:"max_drawdown"`
    Sharp       float64   `gorm:"not null" json:"sharp"`
    Datetime    time.Time `gorm:"autoCreateTime" json:"datetime"`
}

func (Backtest) TableName() string {
    return "backtests"
}

type Signal struct {
    ID              uint       `gorm:"primaryKey" json:"id"`
    Strategy        string     `gorm:"size:100;uniqueIndex;not null" json:"strategy"`
    LongSignal      string     `gorm:"size:20;not null" json:"long_signal"`
    ShortSignal     string     `gorm:"size:20;not null" json:"short_signal"`
    Mode            string     `gorm:"size:20;not null" json:"mode"`
    Status          string     `gorm:"size:20;not null" json:"status"`
    Fiat            float64    `gorm:"not null" json:"fiat"`
    Active          float64    `gorm:"not null" json:"active"`
    Deposit         float64    `gorm:"not null" json:"deposit"`
    StopLoss        float64    `gorm:"not null" json:"stop_loss"`
    WeightPortfolio float64    `gorm:"not null" json:"weight_portfolio"`
    AdjDeposite     float64    `gorm:"not null" json:"adj_deposite"`
    CurrentPosition float64    `gorm:"not null" json:"current_position"`
    Datetime        time.Time  `gorm:"autoCreateTime" json:"datetime"`
    Trades          []Trade    `gorm:"foreignKey:SignalID;constraint:OnDelete:CASCADE" json:"trades,omitempty"`
    AdjTrades       []TradeADJ `gorm:"foreignKey:SignalID;constraint:OnDelete:CASCADE" json:"adj_trades,omitempty"`
}

func (Signal) TableName() string {
    return "signals"
}

type Trade struct {
    ID          uint      `gorm:"primaryKey" json:"id"`
    SignalID    uint      `gorm:"not null;index" json:"signal_id"`
    LongSignal  string    `gorm:"size:20;not null" json:"long_signal"`
    ShortSignal string    `gorm:"size:20;not null" json:"short_signal"`
    Fiat        float64   `gorm:"not null" json:"fiat"`
    Active      float64   `gorm:"not null" json:"active"`
    Deposit     float64   `gorm:"not null" json:"deposit"`
    Datetime    time.Time `gorm:"autoCreateTime" json:"datetime"`
}

func (Trade) TableName() string {
    return "trades"
}

type TradeADJ struct {
    ID          uint      `gorm:"primaryKey" json:"id"`
    SignalID    uint      `gorm:"not null;index" json:"signal_id"`
    AdjDeposite float64   `gorm:"not null" json:"adj_deposite"`
    Datetime    time.Time `gorm:"autoCreateTime" json:"datetime"`
}

func (TradeADJ) TableName() string {
    return "adj_trades"
}

type CurrentPortfolio struct {
    ID                uint               `gorm:"primaryKey" json:"id"`
    NamePortfolio     string             `gorm:"size:100;uniqueIndex;not null" json:"name_portfolio"`
    Portfolio         float64            `gorm:"not null" json:"portfolio"`
    FullProfit        float64            `gorm:"not null" json:"full_profit"`
    YearProfit        float64            `gorm:"not null" json:"year_profit"`
    MaxDrawdown       float64            `gorm:"not null" json:"max_drawdown"`
    Sharp             float64            `gorm:"not null" json:"sharp"`
    ProfitFactor      float64            `gorm:"not null" json:"profit_factor"`
    Datetime          time.Time          `gorm:"autoCreateTime" json:"datetime"`
    HistoryPortfolios []HistoryPortfolio `gorm:"foreignKey:CurrentPortfolioID;constraint:OnDelete:CASCADE" json:"history_portfolio,omitempty"`
}

func (CurrentPortfolio) TableName() string {
    return "current_portfolio"
}

type HistoryPortfolio struct {
    ID                 uint      `gorm:"primaryKey" json:"id"`
    CurrentPortfolioID uint      `gorm:"not null;index" json:"current_portfolio_id"`
    Portfolio          float64   `gorm:"not null" json:"portfolio"`
    Datetime           time.Time `gorm:"autoCreateTime" json:"datetime"`
}

func (HistoryPortfolio) TableName() string {
    return "history_portfolio"
}



