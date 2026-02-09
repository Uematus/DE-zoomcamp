# Загрузка 6 месяцев данных Yellow Taxi в BigQuery

## 📂 Стратегия: Отдельные таблицы + Объединение

Вы правильно мыслите! План такой:
1. ✅ Загрузить 6 parquet файлов → 6 отдельных таблиц
2. ✅ Объединить их в одну таблицу через SQL
3. ✅ Использовать объединённую таблицу для ДЗ

---

## ШАГ 1: Загрузка всех 6 файлов

### Повторите процесс для каждого месяца:

**Для января (вы уже сделали):**
- Source: Upload → `yellow_tripdata_2024-01.parquet`
- Dataset: `ny_taxi`
- Table name: `yellow_tripdata_2024_01`
- Schema: Auto detect ✅
- CREATE TABLE

**Для февраля:**
- Source: Upload → `yellow_tripdata_2024-02.parquet`
- Dataset: `ny_taxi`
- Table name: `yellow_tripdata_2024_02`
- Schema: Auto detect ✅
- CREATE TABLE

**Для марта:**
- Source: Upload → `yellow_tripdata_2024-03.parquet`
- Dataset: `ny_taxi`
- Table name: `yellow_tripdata_2024_03`
- Schema: Auto detect ✅
- CREATE TABLE

**Для апреля:**
- Source: Upload → `yellow_tripdata_2024-04.parquet`
- Dataset: `ny_taxi`
- Table name: `yellow_tripdata_2024_04`
- Schema: Auto detect ✅
- CREATE TABLE

**Для мая:**
- Source: Upload → `yellow_tripdata_2024-05.parquet`
- Dataset: `ny_taxi`
- Table name: `yellow_tripdata_2024_05`
- Schema: Auto detect ✅
- CREATE TABLE

**Для июня:**
- Source: Upload → `yellow_tripdata_2024-06.parquet`
- Dataset: `ny_taxi`
- Table name: `yellow_tripdata_2024_06`
- Schema: Auto detect ✅
- CREATE TABLE

---

## ШАГ 2: Проверка загруженных таблиц

После загрузки всех 6 файлов выполните этот запрос:

```sql
SELECT
  table_id,
  row_count,
  ROUND(size_bytes/1024/1024, 2) as size_mb
FROM `de-zoomcamp-484910.ny_taxi.__TABLES__`
WHERE table_id LIKE 'yellow_tripdata_2024%'
ORDER BY table_id;
```

**Ожидаемый результат:**
```
table_name                    | row_count | size_mb
------------------------------|-----------|----------
yellow_tripdata_2024_01       | ~2500000  | ~250
yellow_tripdata_2024_02       | ~2300000  | ~230
yellow_tripdata_2024_03       | ~2800000  | ~280
yellow_tripdata_2024_04       | ~2700000  | ~270
yellow_tripdata_2024_05       | ~2900000  | ~290
yellow_tripdata_2024_06       | ~2800000  | ~280
```

Должно быть **6 таблиц**!

---

## ШАГ 3: Объединение всех месяцев в одну таблицу

Теперь создайте **одну большую таблицу** из всех 6 месяцев:

```sql
CREATE OR REPLACE TABLE `de-zoomcamp-484910.ny_taxi.yellow_tripdata` AS
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_01`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_02`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_03`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_04`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_05`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_06`;
```

**⚠️ ВАЖНО:** `UNION ALL` объединяет все строки (включая дубликаты). Это правильно для нашего случая, т.к. каждый месяц содержит уникальные поездки.

---

## ШАГ 4: Создание External Table (VIEW)

Для выполнения ДЗ вам нужна **External Table**. Поскольку у вас нет GCS, создадим **VIEW** как её имитацию:

### Вариант A: VIEW на отдельные месяцы (имитация чтения из 6 файлов)

```sql
CREATE OR REPLACE VIEW `de-zoomcamp-484910.ny_taxi.external_yellow_tripdata` AS
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_01`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_02`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_03`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_04`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_05`
UNION ALL
SELECT * FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata_2024_06`;
```

## ШАГ 5: Проверка результатов

```sql
SELECT 
  COUNT(*) as total_records,
  MIN(tpep_pickup_datetime) as earliest_trip,
  MAX(tpep_pickup_datetime) as latest_trip
FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata;
```

## Создать партиционированную + кластеризованную:
```
-- Create combo table
CREATE OR REPLACE TABLE `de-zoomcamp-484910.ny_taxi.yellow_tripdata_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM de-zoomcamp-484910.ny_taxi.yellow_tripdata
WHERE cast(tpep_dropoff_datetime as date) >= '2024-03-01' and cast(tpep_dropoff_datetime as date) <= '2024-03-15';
```

### Проблема с датами
В итог попадали даты только 2026 года. Преобразование на +2 года ко всем датам - прошло нормально  

```
CREATE OR REPLACE TABLE `de-zoomcamp-484910.ny_taxi.yellow_tripdata_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT 
    * EXCEPT(tpep_dropoff_datetime), 
    TIMESTAMP(DATETIME_ADD(DATETIME(tpep_dropoff_datetime), INTERVAL 2 YEAR)) AS tpep_dropoff_datetime
FROM `de-zoomcamp-484910.ny_taxi.yellow_tripdata`
WHERE tpep_dropoff_datetime >= '2024-03-01' and tpep_dropoff_datetime <= '2024-03-15';
```