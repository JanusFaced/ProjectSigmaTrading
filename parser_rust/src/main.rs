use ccxt_exchanges::binance::Binance;
use ccxt_exchanges::binance::BinanceOptions;
use ccxt_core::types::default_type::{DefaultType, DefaultSubType};
use ccxt_rust::prelude::*;
use std::collections::HashMap;
use anyhow::{Result, anyhow};
use tokio::time::sleep;
use chrono::Duration as ChronoDuration;
use std::time::Duration as StdDuration; 

#[tokio::main]
async fn main() -> Result<()> {
    println!("=== Start parsing! ===\n");

    let mode = "imitation".to_string();

    let list_symbol = vec!["ETH", "BNB", "SOL", "TRX", "ADA"];
    let list_type_market = vec!["futures"];
    let list_name_exchange = vec!["binance"];
    
    let list_factor = vec!["BTC"];
    let list_type_factor = vec!["futures"];
    let list_factor_exchange = vec!["binance"];

    let mut tasks: Vec<HashMap<String, String>> = Vec::new();

    for &name_exchange in &list_name_exchange {
        for &type_market in &list_type_market {
            for &symbol in &list_symbol {
                let mut task = HashMap::new();
                task.insert("mode".to_string(), mode.clone());
                task.insert("nameExchange".to_string(), name_exchange.to_string());
                task.insert("symbol".to_string(), symbol.to_string());
                task.insert("type_market".to_string(), type_market.to_string());
                tasks.push(task);
            }
        }
    }

    for &name_exchange in &list_factor_exchange {
        for &type_market in &list_type_factor {
            for &symbol in &list_factor {
                let mut task = HashMap::new();
                task.insert("mode".to_string(), mode.clone());
                task.insert("nameExchange".to_string(), name_exchange.to_string());
                task.insert("symbol".to_string(), symbol.to_string());
                task.insert("type_market".to_string(), type_market.to_string());
                tasks.push(task);
            }
        }
    }

    let length_combi = tasks.len();
    println!("full lenth combination = {}", length_combi);

    for task in &tasks {
        let result = start_parser(task).await?;
        println!("{}", result);
    }
    
    Ok(())
}

async fn start_parser(task: &HashMap<String, String>) -> Result<i64> {
    println!("Start work cycle!");

    let mode = task.get("mode").ok_or_else(|| anyhow!("mode not found"))?;
    let name_exchange = task.get("nameExchange").ok_or_else(|| anyhow!("nameExchange not found"))?;
    let symbol = task.get("symbol").ok_or_else(|| anyhow!("symbol not found"))?;
    let type_market = task.get("type_market").ok_or_else(|| anyhow!("type_market not found"))?; 

    let (now_much_more_days, name_table) = match mode.as_str() {
        "test" => (
            9999,
            format!("{}_{}_{}", name_exchange, symbol, type_market).to_lowercase()
        ),
        "imitation" | "real" => (
            125,
            format!("short_{}_{}_{}", name_exchange, symbol, type_market).to_lowercase()
        ),
        _ => return Err(anyhow!("Неизвестный режим: {}", mode)),
    };

    let ticker = if type_market == "spot" {
        format!("{}/USDT", symbol)
    } else {
        format!("{}/USDT:USDT", symbol)
    };

    let time_frame = "1m";
    let delta_datetime = ChronoDuration::minutes(1);
    let limit = 1000; 

    println!("\nGenerated config:");
    println!("  now_much_more_days: {}", now_much_more_days);
    println!("  name_table: {}", name_table);
    println!("  ticker: {}", ticker);
    println!("  time_frame: {}", time_frame);
    println!("  delta_datetime: {} minutes", delta_datetime.num_minutes());
    println!("  limit: {}", limit);

    let exchange = setup_exchange(type_market).await?;

    let ohlcv_data = exchange
        .fetch_ohlcv(&ticker, &time_frame, None, None, None)
        .await?;

    print_ohlcv_table(&ohlcv_data);

    sleep(StdDuration::from_secs(3)).await;

    Ok(0)
}

async fn setup_exchange(type_market: &str) -> Result<Binance> {
    let mut exchange = Binance::builder().build()?;
    
    let options = if type_market == "futures" {
        println!("✅ Настройка Binance на фьючерсы (Swap)");
        BinanceOptions {
            default_type: DefaultType::Swap,  // Для фьючерсов
            default_sub_type: Some(DefaultSubType::Linear), // USDT-маржинированные
            ..Default::default()
        }
    } else {
        println!("✅ Настройка Binance на спот");
        BinanceOptions {
            default_type: DefaultType::Spot,  // Для спота
            ..Default::default()
        }
    };
    
    exchange.set_options(options);
    exchange.load_markets(false).await?;
    println!("✅ Рынки загружены!\n");
    
    Ok(exchange)
}

fn print_ohlcv_table(ohlcv_data: &[OHLCV]) {
    let tail_size = 20;
    println!(
        "{:<20} {:>10} {:>10} {:>10} {:>10} {:>10}",
        "Дата", "Open", "High", "Low", "Close", "Volume"
    );
    println!(
        "{:-<20} {:-<10} {:-<10} {:-<10} {:-<10} {:-<10}",
        "", "", "", "", "", ""
    );
    for candle in ohlcv_data.iter().rev().take(tail_size).rev() {
        let date = chrono::DateTime::from_timestamp_millis(candle.timestamp)
            .unwrap()
            .format("%Y-%m-%d %H:%M");
        
        println!(
            "{:>20} {:>10.2} {:>10.2} {:>10.2} {:>10.2} {:>10.2}",
            date, candle.open, candle.high, candle.low, candle.close, candle.volume
        );
    }
    println!();
}