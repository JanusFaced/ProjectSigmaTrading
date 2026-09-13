-- migrate:up
TRUNCATE TABLE
  short_binance_sol_futures,
  short_binance_avax_futures,
  short_binance_doge_futures,
  short_binance_vet_futures,
  short_binance_ada_futures,
  short_binance_eth_futures,
  short_binance_bnb_futures,
  short_binance_zec_futures,
  short_binance_btc_futures,
  short_binance_xrp_futures,
  short_binance_fil_futures
RESTART IDENTITY;

-- migrate:down
SELECT 1;