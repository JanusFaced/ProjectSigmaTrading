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
    ID          uint      `gorm:"primaryKey" json:"id"`
    Strategy    string    `gorm:"size:100;uniqueIndex;not null" json:"strategy"`
    LongSignal  string    `gorm:"size:20;not null" json:"long_signal"`
    ShortSignal string    `gorm:"size:20;not null" json:"short_signal"`
    Mode        string    `gorm:"size:20;not null" json:"mode"`
    Status      string    `gorm:"size:20;not null" json:"status"`
    Fiat        float64   `gorm:"not null" json:"fiat"`
    Active      float64   `gorm:"not null" json:"active"`
    Deposit     float64   `gorm:"not null" json:"deposit"`
    Datetime    time.Time `gorm:"autoCreateTime" json:"datetime"`
    Trades      []Trade   `gorm:"foreignKey:SignalID;constraint:OnDelete:CASCADE" json:"trades,omitempty"`
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