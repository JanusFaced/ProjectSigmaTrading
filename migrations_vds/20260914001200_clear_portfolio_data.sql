-- migrate:up

DELETE FROM history_portfolio
WHERE current_portfolio_id = (
    SELECT id FROM current_portfolio WHERE name_portfolio = 'standart'
)
AND id NOT IN (
    SELECT id FROM (
        SELECT hp.id
        FROM history_portfolio hp
        JOIN current_portfolio cp ON cp.id = hp.current_portfolio_id
        WHERE cp.name_portfolio = 'standart'
        ORDER BY hp.datetime ASC, hp.id ASC
        LIMIT 2
    ) keep_rows
);

-- migrate:down
-- Откат невозможен без бэкапа: удалённые строки не восстановить.
-- Сделайте pg_dump перед применением.