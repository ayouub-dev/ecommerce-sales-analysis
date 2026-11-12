
-- 1) Création de la table (si import direct du CSV)
CREATE TABLE IF NOT EXISTS ventes (
    order_id          INT PRIMARY KEY,
    order_date        DATE NOT NULL,
    region            VARCHAR(50),
    category          VARCHAR(50),
    customer_segment  VARCHAR(30),
    channel           VARCHAR(30),
    quantity          INT,
    unit_price        NUMERIC(10,2),
    discount_pct      NUMERIC(4,2),
    revenue           NUMERIC(10,2),
    profit            NUMERIC(10,2)
);

-- \copy ventes FROM 'data/ventes_ecommerce_2024_2026.csv' DELIMITER ',' CSV HEADER;

-- 2) CA et marge par catégorie, triés par CA décroissant
SELECT
    category,
    SUM(revenue)                              AS ca_total,
    SUM(profit)                               AS profit_total,
    ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS marge_pct
FROM ventes
GROUP BY category
ORDER BY ca_total DESC;

-- 3) Impact du taux de remise sur la marge moyenne
SELECT
    discount_pct,
    COUNT(*)                                     AS nb_commandes,
    ROUND(100.0 * AVG(profit / NULLIF(revenue, 0)), 1) AS marge_moyenne_pct
FROM ventes
GROUP BY discount_pct
ORDER BY discount_pct;

-- 4) CA mensuel (évolution dans le temps)
SELECT
    DATE_TRUNC('month', order_date)::date AS mois,
    SUM(revenue)                          AS ca,
    SUM(profit)                           AS profit
FROM ventes
GROUP BY mois
ORDER BY mois;

-- 5) Top et bottom région par CA
SELECT region, SUM(revenue) AS ca_total
FROM ventes
GROUP BY region
ORDER BY ca_total DESC;

-- 6) CA par segment client et canal (équivalent de la heatmap)
SELECT
    customer_segment,
    channel,
    SUM(revenue) AS ca_total
FROM ventes
GROUP BY customer_segment, channel
ORDER BY customer_segment, ca_total DESC;

-- 7) Panier moyen par segment client
SELECT
    customer_segment,
    COUNT(*)                         AS nb_commandes,
    ROUND(AVG(revenue), 2)           AS panier_moyen
FROM ventes
GROUP BY customer_segment
ORDER BY panier_moyen DESC;
