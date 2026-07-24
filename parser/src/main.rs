use ccxt_exchanges::binance::Binance;
use ccxt_exchanges::binance::BinanceOptions;
use ccxt_core::types::default_type::{DefaultType, DefaultSubType};
use ccxt_rust::prelude::*;
use std::collections::{HashMap, HashSet};
use anyhow::{Result, anyhow};
use tokio::time::sleep;
use chrono::Duration as ChronoDuration;
use chrono::{DateTime, Utc, TimeZone, NaiveDateTime};
use std::time::Duration as StdDuration; 
use sqlx::postgres::PgPool;

#[tokio::main]
async fn main() -> Result<()> {
    println!(" <<<< Start RUST parser >>>> \n");
    let mode = std::env::var("GLOBAL_WORK_MODE").expect("GLOBAL_WORK_MODE must be set");

    let value_pause = if mode == "imitation" || mode == "real" {
        60
    } else {
        1000
    };

    loop {
        println!(" === Start parsing! === \n");

        let list_symbol = vec!["ETH", "BNB", "SOL", "TRX", "ADA"];
        //let list_symbol = vec!["XRP", "LINK", "HYPE", "RE", "BOT"];
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
            println!("result = {}.", result);
        }

        println!("Start pause {} seconds!", value_pause);
        sleep(StdDuration::from_secs(value_pause)).await;
    }
    
    Ok(())
}

async fn start_parser(task: &HashMap<String, String>) -> Result<i64> {

    println!("Make connect to Postgres!");
    let user = std::env::var("DB_USER").expect("DB_USER must be set");
    let password = std::env::var("DB_PASSWORD").expect("DB_PASSWORD must be set");
    let host = std::env::var("DB_HOST").expect("DB_HOST must be set");
    let port = std::env::var("DB_PORT").unwrap_or_else(|_| "5432".to_string());
    let name = std::env::var("DB_NAME").expect("DB_NAME must be set");
    let database_url = format!("postgres://{}:{}@{}:{}/{}", user, password, host, port, name);
    let pool = PgPool::connect(&database_url).await?;

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

    let exchange = setup_exchange(type_market).await?;

    let initial_datetime = get_initial_datetime(
        &pool,
        &name_table,
        mode,
        now_much_more_days
    ).await?;

    println!("{} | Start parsing {} from {}", name_table, symbol, initial_datetime);
    let mut current_datetime = initial_datetime;
    let mut collected: Vec<(DateTime<Utc>, f64, f64, f64, f64, f64)> = Vec::new();
    loop {
        let since = Some(current_datetime.timestamp_millis());
        let ohlcv_data = exchange
            .fetch_ohlcv(&ticker, &time_frame, since, Some(limit), None)
            .await?;

        if ohlcv_data.is_empty() {
            println!("⏹️ Данные закончились, выходим из цикла");
            break;
        }

        for candle in &ohlcv_data {
            let dt = DateTime::from_timestamp_millis(candle.timestamp)
                .ok_or_else(|| anyhow!("Неверный timestamp"))?;
            
            collected.push((
                dt,
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume
            ));
        }

        let last_candle = ohlcv_data.last().unwrap();
        let last_dt = DateTime::from_timestamp_millis(last_candle.timestamp)
            .ok_or_else(|| anyhow!("Неверный timestamp"))?;
        
        current_datetime = last_dt + delta_datetime;
        let now_datetime = Utc::now();

        println!("📅 {} <=> {}", name_table, last_dt);

        if current_datetime >= now_datetime {
            println!("⏹️ Достигнут текущий момент, выходим из цикла");
            break;
        }

        sleep(StdDuration::from_millis(500)).await;

    }

    if collected.len() > 1 {
        collected.pop();
        println!("🗑️ Удалена последняя незавершенная свеча");
    }

    if collected.len() > 1 {
        println!("✅ Всего собрано {} свечей. Начинаем удаление дубликатов и заполнение пропусков!", collected.len());
        remove_duplicates_keep_last(&mut collected);
        fill_gaps(&mut collected);

        println!("После очистки данных у нас {} свечей! Начинаем запись в базу данных!", collected.len());
        save_to_database(&pool, &name_table, &collected, mode, now_much_more_days).await?;

        println!("Запись в базу данных произведена! Заканчиваем рабочий цикл!");

    } else {
        println!("Новых данных нет!");
    }

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

async fn get_initial_datetime(
        pool: &PgPool,
        name_table: &str,
        mode: &str,
        now_much_more_days: i64,
    ) -> Result<DateTime<Utc>> {

    let query = format!("SELECT MAX(datetime) FROM {}", name_table);
    let result: Option<NaiveDateTime> = sqlx::query_scalar(&query)
        .fetch_optional(pool)
        .await?;

    match result {
        Some(last_date) => {
            let last_date_utc = DateTime::<Utc>::from_naive_utc_and_offset(last_date, Utc);
            println!("✅ Таблица есть, последняя дата: {}", last_date_utc);
            Ok(last_date_utc + ChronoDuration::minutes(1))
        }
        None => {
            println!("⚠️ Таблицы нет, создаём с начальной даты");
            let start_date = if mode == "test" {
                Utc.with_ymd_and_hms(2017, 1, 1, 0, 0, 0).unwrap()
            } else {
                Utc::now() - ChronoDuration::days(now_much_more_days)
            };
            Ok(start_date)
        }
    }
}

fn remove_duplicates_keep_last(candles: &mut Vec<(DateTime<Utc>, f64, f64, f64, f64, f64)>) {
    let initial_len = candles.len();
    
    candles.sort_by_key(|c| c.0);
    
    let mut i = 0;
    while i + 1 < candles.len() {
        if candles[i].0 == candles[i + 1].0 {
            candles.remove(i);
        } else {
            i += 1;
        }
    }
    
    let removed = initial_len - candles.len();
    if removed > 0 {
        println!("🗑️ Удалено {} дубликатов (сохранены последние)", removed);
    }
    println!("📊 Осталось {} свечей", candles.len());
}

fn fill_gaps(candles: &mut Vec<(DateTime<Utc>, f64, f64, f64, f64, f64)>) {
    if candles.len() < 2 {
        return;
    }

    candles.sort_by_key(|c| c.0);
    
    let mut filled = Vec::new();
    let step = ChronoDuration::minutes(1);
    let mut gaps_filled = 0;
    
    for i in 0..candles.len() - 1 {
        let current = &candles[i];
        let next = &candles[i + 1];
        
        filled.push(current.clone());
        
        let diff = next.0 - current.0;
        let missing_count = (diff.num_minutes() - 1) as usize;
        
        if missing_count > 0 {
            gaps_filled += missing_count;
            println!(
                "⚠️ Пропуск: {} минут между {} и {}",
                missing_count + 1,
                current.0.format("%Y-%m-%d %H:%M"),
                next.0.format("%Y-%m-%d %H:%M")
            );
            
            for j in 1..=missing_count {
                let gap_dt = current.0 + ChronoDuration::minutes(j as i64);
                filled.push((
                    gap_dt,
                    current.1,  // open
                    current.2,  // high
                    current.3,  // low
                    current.4,  // close
                    current.5,  // volume
                ));
            }
        }
    }
    
    if let Some(last) = candles.last() {
        filled.push(last.clone());
    }
    
    *candles = filled;
    println!("✅ Заполнено {} пропусков", gaps_filled);
    println!("📊 Всего свечей: {}", candles.len());
}

async fn save_to_database(
        pool: &PgPool,
        name_table: &str,
        candles: &Vec<(DateTime<Utc>, f64, f64, f64, f64, f64)>,
        mode: &str,
        now_much_more_days: i64,
    ) -> Result<()> {

    let create_sql = format!(
        "CREATE TABLE IF NOT EXISTS {} (
            datetime TIMESTAMP PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume FLOAT
        )",
        name_table
    );
    sqlx::query(&create_sql).execute(pool).await?;
    println!("✅ Таблица {} создана/проверена", name_table);

    println!("📝 Начинаем массовую вставку {} записей...", candles.len());
    let mut inserted_count = 0;
    let chunk_size = 1000;
    for chunk in candles.chunks(chunk_size) {
        let mut query_builder = String::from("INSERT INTO ");
        query_builder.push_str(name_table);
        query_builder.push_str(" (datetime, open, high, low, close, volume) VALUES ");
        
        for (i, _) in chunk.iter().enumerate() {
            let base = i * 6 + 1;
            query_builder.push_str(&format!(
                "(${}, ${}, ${}, ${}, ${}, ${})",
                base, base+1, base+2, base+3, base+4, base+5
            ));
            if i < chunk.len() - 1 {
                query_builder.push_str(", ");
            }
        }
        
        let mut query = sqlx::query(&query_builder);
        for candle in chunk {
            query = query
                .bind(candle.0)
                .bind(candle.1)
                .bind(candle.2)
                .bind(candle.3)
                .bind(candle.4)
                .bind(candle.5);
        }
        
        match query.execute(pool).await {
            Ok(result) => {
                inserted_count += result.rows_affected();
                println!("  📦 Чанк: {} записей вставлено", result.rows_affected());
            }
            Err(e) => {
                if e.to_string().contains("duplicate key") {
                    println!("  ⚠️ Чанк содержит дубликаты, пропускаем");
                } else {
                    return Err(e.into());
                }
            }
        }
    }
    println!("✅ Всего вставлено {} новых записей", inserted_count);

    if mode == "imitation" || mode == "real" {
        let cutoff_date = Utc::now() - ChronoDuration::days(now_much_more_days);
        
        let delete_sql = format!(
            "DELETE FROM {}
            WHERE datetime < $1",
            name_table
        );
        
        let result = sqlx::query(&delete_sql)
            .bind(cutoff_date)
            .execute(pool)
            .await?;
        
        let deleted_rows = result.rows_affected();
        if deleted_rows > 0 {
            println!("🗑️ Удалено {} старых записей (до {})", 
                deleted_rows, 
                cutoff_date.format("%Y-%m-%d %H:%M")
            );
        } else {
            println!("✅ Старых записей для удаления нет");
        }
    }

    println!("✅ Таблица {} успешно обновлена! Начинаем оценку целостности данных:", name_table);

    Ok(())
}

