ORDERS_SETUP = """
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    price NUMERIC
);

INSERT INTO orders (id, customer_id, item, price) VALUES
(1, 1, 'Book', 20),
(2, 1, 'Pen', 5),
(3, 1, 'Book', 20),
(4, 2, 'Laptop', 1000),
(5, 2, 'Mouse', 25),
(6, 3, 'Keyboard', NULL),
(7, 3, 'Mouse', 25),
(8, 4, 'Monitor', 200),
(9, 4, 'Monitor', 200);
"""

CUSTOMERS_ORDERS_SETUP = """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    item TEXT NOT NULL,
    price NUMERIC
);

INSERT INTO customers (id, name) VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie'),
(4, 'Diana');

INSERT INTO orders (id, customer_id, item, price) VALUES
(1, 1, 'Book', 20),
(2, 1, 'Pen', 5),
(3, 2, 'Laptop', 1000),
(4, 2, 'Mouse', 25),
(5, 3, 'Keyboard', 50),
(6, 4, 'Monitor', 200);
"""

DRIVERS_SETUP = """
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE trips (
    id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    distance_km NUMERIC,
    price NUMERIC,
    rating NUMERIC
);

INSERT INTO drivers (id, name) VALUES
(1, 'Alex'),
(2, 'Maria'),
(3, 'John'),
(4, 'Sarah');

INSERT INTO trips (id, driver_id, distance_km, price, rating) VALUES
(1, 1, 10, 20, 5),
(2, 1, 5, 12, 4),
(3, 2, 8, 16, 3),
(4, 2, 15, 30, 4),
(5, 3, 20, 45, 5),
(6, 4, NULL, NULL, NULL);
"""

PRODUCTS_SETUP = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sale_price NUMERIC NOT NULL
);

CREATE TABLE returns (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);

INSERT INTO products (id, name, category) VALUES
(1, 'Laptop', 'Electronics'),
(2, 'Mouse', 'Electronics'),
(3, 'Notebook', 'Stationery'),
(4, 'Pen', 'Stationery'),
(5, 'Chair', 'Office');

INSERT INTO sales (id, product_id, quantity, sale_price) VALUES
(1, 1, 2, 1000),
(2, 2, 10, 25),
(3, 3, 20, 5),
(4, 4, 50, 2),
(5, 5, 3, 120);

INSERT INTO returns (id, product_id, quantity) VALUES
(1, 2, 2),
(2, 4, 10),
(3, 5, 1);
"""

CONTENT_SETUP = """
CREATE TABLE creators (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE videos (
    id INTEGER PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    title TEXT NOT NULL
);

CREATE TABLE views (
    id INTEGER PRIMARY KEY,
    video_id INTEGER NOT NULL,
    watch_time INTEGER NOT NULL
);

INSERT INTO creators (id, name) VALUES
(1, 'Leo'),
(2, 'Mia'),
(3, 'Noah'),
(4, 'Zara');

INSERT INTO videos (id, creator_id, title) VALUES
(1, 1, 'V1'),
(2, 1, 'V2'),
(3, 2, 'V3'),
(4, 3, 'V4');

INSERT INTO views (id, video_id, watch_time) VALUES
(1, 1, 10),
(2, 1, 15),
(3, 2, 20),
(4, 3, 5),
(5, 3, 10);
"""


SEED_TASKS = [
    {
        "slug": "orders-over-50",
        "title": "Orders Over 50",
        "prompt": "The sales team wants to review high-value order lines. Show the expensive orders first, with enough detail to identify the customer and item.",
        "setup_sql": ORDERS_SETUP,
        "expected_sql": "SELECT customer_id, item, price FROM orders WHERE price > 50 ORDER BY price DESC",
        "solution_sql": "SELECT customer_id, item, price\nFROM orders\nWHERE price > 50\nORDER BY price DESC;",
        "hint": "Use WHERE before ORDER BY.",
        "hint2": "Show customer_id, item, and price. Keep only rows where price is greater than 50, then sort from highest price to lowest.",
        "concepts": ["where", "order by"],
        "difficulty": 1,
        "estimated_minutes": 4,
        "sort_order": 10,
    },
    {
        "slug": "count-null-prices",
        "title": "COUNT And NULL",
        "prompt": "Before reporting revenue, the data team wants to check whether every order has a price. Produce a one-row data quality summary.",
        "setup_sql": ORDERS_SETUP,
        "expected_sql": "SELECT COUNT(*) AS total_orders, COUNT(price) AS priced_orders FROM orders",
        "solution_sql": "SELECT COUNT(*) AS total_orders, COUNT(price) AS priced_orders\nFROM orders;",
        "hint": "COUNT(*) and COUNT(column) are not the same when NULL exists.",
        "hint2": "Create one row with total_orders using COUNT(*) and priced_orders using COUNT(price). COUNT(price) ignores NULL prices.",
        "concepts": ["count", "null"],
        "difficulty": 1,
        "estimated_minutes": 4,
        "sort_order": 20,
    },
    {
        "slug": "total-spent-per-customer",
        "title": "Total Spent Per Customer",
        "prompt": "Finance needs a customer spending summary. Include customers even when their prices do not add up to a real value, and make the report easy to scan by customer.",
        "setup_sql": ORDERS_SETUP,
        "expected_sql": "SELECT customer_id, COALESCE(SUM(price), 0) AS total_spent FROM orders GROUP BY customer_id ORDER BY customer_id",
        "solution_sql": "SELECT customer_id, COALESCE(SUM(price), 0) AS total_spent\nFROM orders\nGROUP BY customer_id\nORDER BY customer_id;",
        "hint": "SUM ignores NULL. COALESCE changes a NULL result to 0.",
        "hint2": "Group by customer_id. Calculate total_spent with COALESCE(SUM(price), 0). Sort by customer_id.",
        "concepts": ["group by", "sum", "coalesce"],
        "difficulty": 2,
        "estimated_minutes": 5,
        "sort_order": 30,
    },
    {
        "slug": "unique-items-per-customer",
        "title": "Unique Items Per Customer",
        "prompt": "Marketing wants to know which customers buy the widest variety of products. Rank customers by product variety.",
        "setup_sql": ORDERS_SETUP,
        "expected_sql": "SELECT customer_id, COUNT(DISTINCT item) AS unique_items FROM orders GROUP BY customer_id ORDER BY unique_items DESC, customer_id ASC",
        "solution_sql": "SELECT customer_id, COUNT(DISTINCT item) AS unique_items\nFROM orders\nGROUP BY customer_id\nORDER BY unique_items DESC, customer_id ASC;",
        "hint": "DISTINCT can live inside COUNT.",
        "hint2": "Group by customer_id and count distinct item values as unique_items. Sort by unique_items descending, then customer_id ascending.",
        "concepts": ["count distinct", "group by"],
        "difficulty": 2,
        "estimated_minutes": 5,
        "sort_order": 40,
    },
    {
        "slug": "customers-spent-over-100",
        "title": "Customers Over 100",
        "prompt": "The account manager wants a shortlist of customers worth extra attention based on total spend above 100.",
        "setup_sql": ORDERS_SETUP,
        "expected_sql": "SELECT customer_id, SUM(price) AS total_spent FROM orders GROUP BY customer_id HAVING SUM(price) > 100 ORDER BY total_spent DESC",
        "solution_sql": "SELECT customer_id, SUM(price) AS total_spent\nFROM orders\nGROUP BY customer_id\nHAVING SUM(price) > 100\nORDER BY total_spent DESC;",
        "hint": "Use HAVING when filtering aggregate results.",
        "hint2": "Group by customer_id, calculate total_spent with SUM(price), keep only totals greater than 100, then sort highest first.",
        "concepts": ["group by", "having"],
        "difficulty": 2,
        "estimated_minutes": 5,
        "sort_order": 50,
    },
    {
        "slug": "customer-order-names",
        "title": "Customer Order Names",
        "prompt": "Support wants an order list that uses customer names instead of numeric IDs, with the highest-price orders at the top.",
        "setup_sql": CUSTOMERS_ORDERS_SETUP,
        "expected_sql": "SELECT c.name AS customer_name, o.item, o.price FROM customers c JOIN orders o ON c.id = o.customer_id ORDER BY o.price DESC",
        "solution_sql": "SELECT c.name AS customer_name, o.item, o.price\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nORDER BY o.price DESC;",
        "hint": "Join customers.id to orders.customer_id.",
        "hint2": "Join customers to orders. Show customer name as customer_name, item, and price. Sort by order price descending.",
        "concepts": ["join", "order by"],
        "difficulty": 2,
        "estimated_minutes": 5,
        "sort_order": 60,
    },
    {
        "slug": "customer-total-spending",
        "title": "Customer Spending Report",
        "prompt": "Management wants a ranked customer spending report using readable customer names.",
        "setup_sql": CUSTOMERS_ORDERS_SETUP,
        "expected_sql": "SELECT c.name AS customer_name, SUM(o.price) AS total_spent FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.name ORDER BY total_spent DESC",
        "solution_sql": "SELECT c.name AS customer_name, SUM(o.price) AS total_spent\nFROM customers c\nLEFT JOIN orders o ON c.id = o.customer_id\nGROUP BY c.id, c.name\nORDER BY total_spent DESC;",
        "hint": "Group by the customer identity after the join.",
        "hint2": "Use a LEFT JOIN from customers to orders. Group by customer id and name. Show customer_name and total_spent, sorted highest first.",
        "concepts": ["left join", "group by"],
        "difficulty": 3,
        "estimated_minutes": 6,
        "sort_order": 70,
    },
    {
        "slug": "driver-earnings-report",
        "title": "Driver Earnings Report",
        "prompt": "Operations needs a driver earnings dashboard. In this dataset, trip price is the earning amount. Include drivers with no completed paid trips so no one disappears from the report.",
        "setup_sql": DRIVERS_SETUP,
        "expected_sql": "SELECT d.name AS driver_name, COUNT(t.price) AS total_trips, SUM(t.price) AS total_earnings, AVG(t.price) AS avg_trip_price FROM drivers d LEFT JOIN trips t ON d.id = t.driver_id GROUP BY d.id, d.name ORDER BY total_earnings DESC NULLS LAST",
        "solution_sql": "SELECT d.name AS driver_name,\n       COUNT(t.price) AS total_trips,\n       SUM(t.price) AS total_earnings,\n       AVG(t.price) AS avg_trip_price\nFROM drivers d\nLEFT JOIN trips t ON d.id = t.driver_id\nGROUP BY d.id, d.name\nORDER BY total_earnings DESC NULLS LAST;",
        "hint": "Treat trips.price as the money earned for a completed paid trip. COUNT(t.price) ignores Sarah's NULL trip price.",
        "hint2": "Build a report with 4 columns: driver_name, total_trips, total_earnings, and avg_trip_price. Start from drivers, LEFT JOIN trips, group by driver, and sort total_earnings from highest to lowest with NULL totals last.",
        "concepts": ["left join", "aggregate", "null"],
        "difficulty": 3,
        "estimated_minutes": 6,
        "sort_order": 80,
    },
    {
        "slug": "active-drivers-distance",
        "title": "Drivers Above 20 KM",
        "prompt": "Dispatch wants to identify drivers with more than 20 km of completed activity and compare them by distance.",
        "setup_sql": DRIVERS_SETUP,
        "expected_sql": "SELECT d.name AS driver_name, SUM(t.distance_km) AS total_distance, COUNT(t.id) AS total_trips FROM drivers d JOIN trips t ON d.id = t.driver_id GROUP BY d.id, d.name HAVING SUM(t.distance_km) > 20 ORDER BY total_distance DESC",
        "solution_sql": "SELECT d.name AS driver_name,\n       SUM(t.distance_km) AS total_distance,\n       COUNT(t.id) AS total_trips\nFROM drivers d\nJOIN trips t ON d.id = t.driver_id\nGROUP BY d.id, d.name\nHAVING SUM(t.distance_km) > 20\nORDER BY total_distance DESC;",
        "hint": "Filter by SUM(distance_km), not by COUNT(distance_km).",
        "hint2": "Join drivers to trips, group by driver, calculate total_distance and total_trips. Use HAVING SUM(distance_km) > 20.",
        "concepts": ["having", "sum", "join"],
        "difficulty": 3,
        "estimated_minutes": 6,
        "sort_order": 90,
    },
    {
        "slug": "net-revenue-per-product",
        "title": "Net Revenue Per Product",
        "prompt": "The ecommerce team wants a product revenue report that accounts for returns and still includes products without return rows.",
        "setup_sql": PRODUCTS_SETUP,
        "expected_sql": "SELECT p.name AS product_name, COALESCE(s.gross_revenue, 0) AS gross_revenue, COALESCE(r.returned_items, 0) AS returned_items, COALESCE(s.gross_revenue, 0) - COALESCE(r.returned_items, 0) AS net_revenue FROM products p LEFT JOIN (SELECT product_id, SUM(quantity * sale_price) AS gross_revenue FROM sales GROUP BY product_id) s ON p.id = s.product_id LEFT JOIN (SELECT product_id, SUM(quantity) AS returned_items FROM returns GROUP BY product_id) r ON p.id = r.product_id ORDER BY net_revenue DESC",
        "solution_sql": "SELECT p.name AS product_name,\n       COALESCE(s.gross_revenue, 0) AS gross_revenue,\n       COALESCE(r.returned_items, 0) AS returned_items,\n       COALESCE(s.gross_revenue, 0) - COALESCE(r.returned_items, 0) AS net_revenue\nFROM products p\nLEFT JOIN (\n    SELECT product_id, SUM(quantity * sale_price) AS gross_revenue\n    FROM sales\n    GROUP BY product_id\n) s ON p.id = s.product_id\nLEFT JOIN (\n    SELECT product_id, SUM(quantity) AS returned_items\n    FROM returns\n    GROUP BY product_id\n) r ON p.id = r.product_id\nORDER BY net_revenue DESC;",
        "hint": "Aggregate sales and returns separately, then join those summaries to products.",
        "hint2": "Build one sales summary by product and one returns summary by product. Join both to products. Show product_name, gross_revenue, returned_items, and net_revenue.",
        "concepts": ["subquery", "left join", "coalesce"],
        "difficulty": 4,
        "estimated_minutes": 8,
        "sort_order": 100,
    },
    {
        "slug": "creator-performance",
        "title": "Creator Performance",
        "prompt": "The content team wants to compare creator reach. Include creators who have not published videos yet.",
        "setup_sql": CONTENT_SETUP,
        "expected_sql": "SELECT c.name AS creator_name, COUNT(DISTINCT v.id) AS total_videos, COALESCE(SUM(vi.watch_time), 0) AS total_watch_time FROM creators c LEFT JOIN videos v ON c.id = v.creator_id LEFT JOIN views vi ON v.id = vi.video_id GROUP BY c.id, c.name ORDER BY total_watch_time DESC",
        "solution_sql": "SELECT c.name AS creator_name,\n       COUNT(DISTINCT v.id) AS total_videos,\n       COALESCE(SUM(vi.watch_time), 0) AS total_watch_time\nFROM creators c\nLEFT JOIN videos v ON c.id = v.creator_id\nLEFT JOIN views vi ON v.id = vi.video_id\nGROUP BY c.id, c.name\nORDER BY total_watch_time DESC;",
        "hint": "Use COUNT(DISTINCT v.id), because a video can have many view rows.",
        "hint2": "Start from creators, LEFT JOIN videos, then LEFT JOIN views. Group by creator. Count distinct videos and sum watch_time with COALESCE.",
        "concepts": ["left join", "count distinct", "coalesce"],
        "difficulty": 4,
        "estimated_minutes": 7,
        "sort_order": 110,
    },
    {
        "slug": "high-engagement-creators",
        "title": "High Engagement Creators",
        "prompt": "Leadership wants to know which creators beat the platform-wide average watch time.",
        "setup_sql": CONTENT_SETUP,
        "expected_sql": "SELECT c.name AS creator_name, AVG(vi.watch_time) AS avg_watch_time FROM creators c LEFT JOIN videos v ON c.id = v.creator_id LEFT JOIN views vi ON v.id = vi.video_id GROUP BY c.id, c.name HAVING AVG(vi.watch_time) > (SELECT AVG(watch_time) FROM views) ORDER BY avg_watch_time DESC",
        "solution_sql": "SELECT c.name AS creator_name,\n       AVG(vi.watch_time) AS avg_watch_time\nFROM creators c\nLEFT JOIN videos v ON c.id = v.creator_id\nLEFT JOIN views vi ON v.id = vi.video_id\nGROUP BY c.id, c.name\nHAVING AVG(vi.watch_time) > (\n    SELECT AVG(watch_time)\n    FROM views\n)\nORDER BY avg_watch_time DESC;",
        "hint": "The overall average can come from a scalar subquery in HAVING.",
        "hint2": "Calculate each creator's AVG(watch_time). Compare it in HAVING to SELECT AVG(watch_time) FROM views. Sort by avg_watch_time descending.",
        "concepts": ["having", "subquery", "avg"],
        "difficulty": 4,
        "estimated_minutes": 8,
        "sort_order": 120,
    },
]


def three_table_setup(
    parent_table,
    child_table,
    event_table,
    parent_names,
    child_label,
    event_metric,
    children,
    events,
):
    parent_key = singular_name(parent_table)
    child_key = singular_name(child_table)
    parent_values = ",\n".join(
        f"({index + 1}, '{name}')" for index, name in enumerate(parent_names)
    )
    child_values = ",\n".join(
        f"({index + 1}, {parent_id}, '{label}')"
        for index, (parent_id, label) in enumerate(children)
    )
    event_values = ",\n".join(
        f"({index + 1}, {child_id}, {metric})"
        for index, (child_id, metric) in enumerate(events)
    )
    return f"""
CREATE TABLE {parent_table} (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE {child_table} (
    id INTEGER PRIMARY KEY,
    {parent_key}_id INTEGER NOT NULL,
    {child_label} TEXT NOT NULL
);

CREATE TABLE {event_table} (
    id INTEGER PRIMARY KEY,
    {child_key}_id INTEGER NOT NULL,
    {event_metric} NUMERIC NOT NULL
);

INSERT INTO {parent_table} (id, name) VALUES
{parent_values};

INSERT INTO {child_table} (id, {parent_key}_id, {child_label}) VALUES
{child_values};

INSERT INTO {event_table} (id, {child_key}_id, {event_metric}) VALUES
{event_values};
"""


def singular_name(table_name):
    if table_name.endswith("ies"):
        return f"{table_name[:-3]}y"
    if table_name.endswith("sses"):
        return table_name[:-2]
    if table_name.endswith("ses"):
        return table_name[:-2]
    if table_name.endswith("s"):
        return table_name[:-1]
    return table_name


def scenario_tasks(
    *,
    key,
    title,
    setup_sql,
    parent_table,
    child_table,
    event_table,
    child_label,
    metric,
    parent_label,
    child_count_label,
    metric_total_label,
    base_sort,
):
    parent_id = f"{singular_name(parent_table)}_id"
    child_id = f"{singular_name(child_table)}_id"
    return [
        {
            "slug": f"{key}-summary",
            "title": f"{title} Summary",
            "prompt": f"The team needs a complete {title.lower()} performance summary. Include entries with no {child_table} yet and rank by total activity.",
            "setup_sql": setup_sql,
            "expected_sql": f"SELECT p.name AS {parent_label}, COUNT(DISTINCT c.id) AS {child_count_label}, COALESCE(SUM(e.{metric}), 0) AS {metric_total_label} FROM {parent_table} p LEFT JOIN {child_table} c ON p.id = c.{parent_id} LEFT JOIN {event_table} e ON c.id = e.{child_id} GROUP BY p.id, p.name ORDER BY {metric_total_label} DESC",
            "solution_sql": f"SELECT p.name AS {parent_label},\n       COUNT(DISTINCT c.id) AS {child_count_label},\n       COALESCE(SUM(e.{metric}), 0) AS {metric_total_label}\nFROM {parent_table} p\nLEFT JOIN {child_table} c ON p.id = c.{parent_id}\nLEFT JOIN {event_table} e ON c.id = e.{child_id}\nGROUP BY p.id, p.name\nORDER BY {metric_total_label} DESC;",
            "hint": "Use LEFT JOIN and COUNT(DISTINCT ...) so rows with no children still appear.",
            "hint2": f"Start from {parent_table}, LEFT JOIN {child_table}, then LEFT JOIN {event_table}. Show {parent_label}, {child_count_label}, and {metric_total_label}. Use COALESCE around the SUM and sort by {metric_total_label} descending.",
            "concepts": ["left join", "count distinct", "coalesce"],
            "difficulty": 3,
            "estimated_minutes": 7,
            "sort_order": base_sort,
        },
        {
            "slug": f"{key}-high-total",
            "title": f"High {title} Totals",
            "prompt": f"Managers want to focus only on high-activity {title.lower()} records where total {metric} is above 30.",
            "setup_sql": setup_sql,
            "expected_sql": f"SELECT p.name AS {parent_label}, SUM(e.{metric}) AS {metric_total_label} FROM {parent_table} p JOIN {child_table} c ON p.id = c.{parent_id} JOIN {event_table} e ON c.id = e.{child_id} GROUP BY p.id, p.name HAVING SUM(e.{metric}) > 30 ORDER BY {metric_total_label} DESC",
            "solution_sql": f"SELECT p.name AS {parent_label},\n       SUM(e.{metric}) AS {metric_total_label}\nFROM {parent_table} p\nJOIN {child_table} c ON p.id = c.{parent_id}\nJOIN {event_table} e ON c.id = e.{child_id}\nGROUP BY p.id, p.name\nHAVING SUM(e.{metric}) > 30\nORDER BY {metric_total_label} DESC;",
            "hint": "Aggregate first, then filter aggregate groups with HAVING.",
            "hint2": f"Join all three tables, group by the parent, calculate SUM({metric}) as {metric_total_label}, filter with HAVING SUM({metric}) > 30, and sort descending.",
            "concepts": ["join", "group by", "having"],
            "difficulty": 3,
            "estimated_minutes": 7,
            "sort_order": base_sort + 1,
        },
        {
            "slug": f"{key}-avg-above-overall",
            "title": f"Above Average {title}",
            "prompt": f"Find the {title.lower()} records performing above the overall average for {metric}.",
            "setup_sql": setup_sql,
            "expected_sql": f"SELECT p.name AS {parent_label}, AVG(e.{metric}) AS avg_{metric} FROM {parent_table} p JOIN {child_table} c ON p.id = c.{parent_id} JOIN {event_table} e ON c.id = e.{child_id} GROUP BY p.id, p.name HAVING AVG(e.{metric}) > (SELECT AVG({metric}) FROM {event_table}) ORDER BY avg_{metric} DESC",
            "solution_sql": f"SELECT p.name AS {parent_label},\n       AVG(e.{metric}) AS avg_{metric}\nFROM {parent_table} p\nJOIN {child_table} c ON p.id = c.{parent_id}\nJOIN {event_table} e ON c.id = e.{child_id}\nGROUP BY p.id, p.name\nHAVING AVG(e.{metric}) > (\n    SELECT AVG({metric})\n    FROM {event_table}\n)\nORDER BY avg_{metric} DESC;",
            "hint": "Compare each group's AVG to a scalar subquery.",
            "hint2": f"Join all three tables and calculate AVG({metric}) per parent as avg_{metric}. Use HAVING to compare that value to the overall AVG({metric}) from {event_table}.",
            "concepts": ["avg", "having", "subquery"],
            "difficulty": 4,
            "estimated_minutes": 8,
            "sort_order": base_sort + 2,
        },
        {
            "slug": f"{key}-child-detail",
            "title": f"{title} Detail Report",
            "prompt": f"The team wants a detailed {title.lower()} report by individual {singular_name(child_table)}, ranked by total activity.",
            "setup_sql": setup_sql,
            "expected_sql": f"SELECT p.name AS {parent_label}, c.{child_label}, COALESCE(SUM(e.{metric}), 0) AS {metric_total_label} FROM {parent_table} p JOIN {child_table} c ON p.id = c.{parent_id} LEFT JOIN {event_table} e ON c.id = e.{child_id} GROUP BY p.id, p.name, c.id, c.{child_label} ORDER BY {metric_total_label} DESC",
            "solution_sql": f"SELECT p.name AS {parent_label},\n       c.{child_label},\n       COALESCE(SUM(e.{metric}), 0) AS {metric_total_label}\nFROM {parent_table} p\nJOIN {child_table} c ON p.id = c.{parent_id}\nLEFT JOIN {event_table} e ON c.id = e.{child_id}\nGROUP BY p.id, p.name, c.id, c.{child_label}\nORDER BY {metric_total_label} DESC;",
            "hint": "Group by the parent and child identity when reporting child-level totals.",
            "hint2": f"Join parent rows to {child_table}, LEFT JOIN {event_table}, then group by parent and child. Show {parent_label}, {child_label}, and {metric_total_label}, sorted descending.",
            "concepts": ["join", "left join", "group by"],
            "difficulty": 3,
            "estimated_minutes": 7,
            "sort_order": base_sort + 3,
        },
    ]


SCENARIOS = [
    {
        "key": "library",
        "title": "Library",
        "parent_table": "authors",
        "child_table": "books",
        "event_table": "borrowings",
        "parent_names": ["Rowling", "Tolkien", "Orwell", "Christie", "Shelley"],
        "child_label": "title",
        "metric": "borrow_days",
        "children": [(1, "Magic One"), (1, "Magic Two"), (2, "Ring"), (3, "Farm"), (4, "Mystery")],
        "events": [(1, 7), (1, 5), (2, 8), (3, 20), (3, 12), (4, 4), (5, 10)],
        "parent_label": "author_name",
        "child_count_label": "total_books",
        "metric_total_label": "total_borrow_days",
    },
    {
        "key": "school",
        "title": "School",
        "parent_table": "teachers",
        "child_table": "classes",
        "event_table": "attendances",
        "parent_names": ["Alice", "Bob", "Carol", "David", "Eva"],
        "child_label": "subject",
        "metric": "students_count",
        "children": [(1, "Math"), (1, "Physics"), (2, "History"), (3, "Biology"), (4, "Art")],
        "events": [(1, 20), (1, 25), (2, 15), (3, 30), (4, 18), (5, 12)],
        "parent_label": "teacher_name",
        "child_count_label": "total_classes",
        "metric_total_label": "total_students",
    },
    {
        "key": "music",
        "title": "Music",
        "parent_table": "artists",
        "child_table": "songs",
        "event_table": "plays",
        "parent_names": ["Jay", "Lina", "Omar", "Eva", "Noah"],
        "child_label": "title",
        "metric": "play_count",
        "children": [(1, "Blue"), (1, "Red"), (2, "Moon"), (3, "Sun"), (4, "Rain")],
        "events": [(1, 10), (1, 5), (2, 7), (3, 3), (4, 25), (5, 4)],
        "parent_label": "artist_name",
        "child_count_label": "total_songs",
        "metric_total_label": "total_plays",
    },
    {
        "key": "restaurant",
        "title": "Restaurant",
        "parent_table": "chefs",
        "child_table": "dishes",
        "event_table": "orders",
        "parent_names": ["Gordon", "Jamie", "Nigella", "Marco", "Asta"],
        "child_label": "dish_name",
        "metric": "quantity",
        "children": [(1, "Steak"), (1, "Burger"), (2, "Pasta"), (3, "Cake"), (4, "Soup")],
        "events": [(1, 2), (1, 3), (2, 1), (3, 40), (4, 9), (5, 12)],
        "parent_label": "chef_name",
        "child_count_label": "total_dishes",
        "metric_total_label": "total_orders",
    },
    {
        "key": "streaming",
        "title": "Streaming",
        "parent_table": "streamers",
        "child_table": "streams",
        "event_table": "donations",
        "parent_names": ["Ninja", "Shroud", "Poki", "Myth", "Luna"],
        "child_label": "title",
        "metric": "amount",
        "children": [(1, "S1"), (1, "S2"), (2, "S3"), (3, "S4"), (4, "S5")],
        "events": [(1, 100), (1, 50), (2, 30), (3, 200), (4, 25), (5, 10)],
        "parent_label": "streamer_name",
        "child_count_label": "total_streams",
        "metric_total_label": "total_donations",
    },
    {
        "key": "projects",
        "title": "Project",
        "parent_table": "employees",
        "child_table": "projects",
        "event_table": "assignments",
        "parent_names": ["Anna", "Mark", "Julia", "Tom", "Ieva"],
        "child_label": "project_name",
        "metric": "hours_worked",
        "children": [(1, "CRM"), (1, "Billing"), (2, "Website"), (3, "Mobile"), (4, "Data")],
        "events": [(1, 12), (1, 8), (2, 15), (3, 20), (4, 6), (5, 25)],
        "parent_label": "employee_name",
        "child_count_label": "total_projects",
        "metric_total_label": "total_hours",
    },
    {
        "key": "education",
        "title": "Education",
        "parent_table": "students",
        "child_table": "courses",
        "event_table": "enrollments",
        "parent_names": ["Emma", "Liam", "Olivia", "Noah", "Mia"],
        "child_label": "course_name",
        "metric": "score",
        "children": [(1, "SQL"), (1, "Python"), (2, "Excel"), (3, "Stats"), (4, "BI")],
        "events": [(1, 85), (1, 90), (2, 70), (3, 60), (4, 95), (5, 50)],
        "parent_label": "student_name",
        "child_count_label": "total_courses",
        "metric_total_label": "total_score",
    },
    {
        "key": "support",
        "title": "Support",
        "parent_table": "agents",
        "child_table": "tickets",
        "event_table": "responses",
        "parent_names": ["Rasa", "Jonas", "Milda", "Tomas", "Greta"],
        "child_label": "topic",
        "metric": "minutes_spent",
        "children": [(1, "Login"), (1, "Billing"), (2, "Bug"), (3, "Refund"), (4, "Setup")],
        "events": [(1, 10), (1, 12), (2, 20), (3, 30), (4, 15), (5, 8)],
        "parent_label": "agent_name",
        "child_count_label": "total_tickets",
        "metric_total_label": "total_minutes",
    },
    {
        "key": "warehouse",
        "title": "Warehouse",
        "parent_table": "categories",
        "child_table": "products",
        "event_table": "shipments",
        "parent_names": ["Electronics", "Stationery", "Furniture", "Kitchen", "Garden"],
        "child_label": "product_name",
        "metric": "units",
        "children": [(1, "Laptop"), (1, "Mouse"), (2, "Pen"), (3, "Chair"), (4, "Cup")],
        "events": [(1, 5), (1, 3), (2, 15), (3, 40), (4, 7), (5, 12)],
        "parent_label": "category_name",
        "child_count_label": "total_products",
        "metric_total_label": "total_units",
    },
    {
        "key": "marketing",
        "title": "Marketing",
        "parent_table": "campaigns",
        "child_table": "ads",
        "event_table": "clicks",
        "parent_names": ["Spring", "Summer", "Autumn", "Winter", "Launch"],
        "child_label": "ad_name",
        "metric": "click_count",
        "children": [(1, "A1"), (1, "A2"), (2, "A3"), (3, "A4"), (4, "A5")],
        "events": [(1, 11), (1, 14), (2, 9), (3, 33), (4, 18), (5, 4)],
        "parent_label": "campaign_name",
        "child_count_label": "total_ads",
        "metric_total_label": "total_clicks",
    },
    {
        "key": "finance",
        "title": "Finance",
        "parent_table": "accounts",
        "child_table": "invoices",
        "event_table": "payments",
        "parent_names": ["Acme", "Beta", "Core", "Delta", "Echo"],
        "child_label": "invoice_code",
        "metric": "amount",
        "children": [(1, "I1"), (1, "I2"), (2, "I3"), (3, "I4"), (4, "I5")],
        "events": [(1, 100), (1, 50), (2, 25), (3, 40), (4, 200), (5, 10)],
        "parent_label": "account_name",
        "child_count_label": "total_invoices",
        "metric_total_label": "total_paid",
    },
    {
        "key": "fitness",
        "title": "Fitness",
        "parent_table": "trainers",
        "child_table": "workouts",
        "event_table": "sessions",
        "parent_names": ["Laura", "Ben", "Marta", "Paul", "Indre"],
        "child_label": "workout_name",
        "metric": "duration_min",
        "children": [(1, "Cardio"), (1, "Strength"), (2, "Yoga"), (3, "Pilates"), (4, "Run")],
        "events": [(1, 30), (1, 25), (2, 45), (3, 20), (4, 50), (5, 15)],
        "parent_label": "trainer_name",
        "child_count_label": "total_workouts",
        "metric_total_label": "total_duration",
    },
    {
        "key": "realestate",
        "title": "Real Estate",
        "parent_table": "agents",
        "child_table": "listings",
        "event_table": "offers",
        "parent_names": ["Adele", "Bruno", "Clara", "Darius", "Elena"],
        "child_label": "property_name",
        "metric": "offer_amount",
        "children": [(1, "Loft"), (1, "Villa"), (2, "Studio"), (3, "Cottage"), (4, "Penthouse")],
        "events": [(1, 120), (1, 80), (2, 45), (3, 60), (4, 200), (5, 25)],
        "parent_label": "agent_name",
        "child_count_label": "total_listings",
        "metric_total_label": "total_offer_amount",
    },
    {
        "key": "healthcare",
        "title": "Healthcare",
        "parent_table": "doctors",
        "child_table": "patients",
        "event_table": "visits",
        "parent_names": ["Nora", "Felix", "Amelia", "Oscar", "Ruta"],
        "child_label": "patient_name",
        "metric": "visit_minutes",
        "children": [(1, "Pat A"), (1, "Pat B"), (2, "Pat C"), (3, "Pat D"), (4, "Pat E")],
        "events": [(1, 20), (1, 30), (2, 25), (3, 15), (4, 40), (5, 10)],
        "parent_label": "doctor_name",
        "child_count_label": "total_patients",
        "metric_total_label": "total_visit_minutes",
    },
    {
        "key": "logistics",
        "title": "Logistics",
        "parent_table": "carriers",
        "child_table": "routes",
        "event_table": "deliveries",
        "parent_names": ["North", "Baltic", "Express", "Cargo", "Metro"],
        "child_label": "route_name",
        "metric": "package_count",
        "children": [(1, "R1"), (1, "R2"), (2, "R3"), (3, "R4"), (4, "R5")],
        "events": [(1, 18), (1, 22), (2, 35), (3, 12), (4, 44), (5, 9)],
        "parent_label": "carrier_name",
        "child_count_label": "total_routes",
        "metric_total_label": "total_packages",
    },
    {
        "key": "gaming",
        "title": "Gaming",
        "parent_table": "players",
        "child_table": "matches",
        "event_table": "scores",
        "parent_names": ["Kai", "Mina", "Rokas", "Sofia", "Taja"],
        "child_label": "match_name",
        "metric": "points",
        "children": [(1, "M1"), (1, "M2"), (2, "M3"), (3, "M4"), (4, "M5")],
        "events": [(1, 12), (1, 18), (2, 25), (3, 7), (4, 40), (5, 16)],
        "parent_label": "player_name",
        "child_count_label": "total_matches",
        "metric_total_label": "total_points",
    },
    {
        "key": "subscriptions",
        "title": "Subscription",
        "parent_table": "plans",
        "child_table": "customers",
        "event_table": "payments",
        "parent_names": ["Basic", "Plus", "Pro", "Business", "Enterprise"],
        "child_label": "customer_name",
        "metric": "amount",
        "children": [(1, "C1"), (1, "C2"), (2, "C3"), (3, "C4"), (4, "C5")],
        "events": [(1, 9), (1, 9), (2, 19), (3, 29), (4, 49), (5, 99)],
        "parent_label": "plan_name",
        "child_count_label": "total_customers",
        "metric_total_label": "total_revenue",
    },
    {
        "key": "events",
        "title": "Events",
        "parent_table": "organizers",
        "child_table": "events",
        "event_table": "tickets",
        "parent_names": ["Muse", "Orbit", "Spark", "Wave", "Peak"],
        "child_label": "event_name",
        "metric": "ticket_count",
        "children": [(1, "Expo"), (1, "Meetup"), (2, "Summit"), (3, "Workshop"), (4, "Party")],
        "events": [(1, 30), (1, 20), (2, 15), (3, 55), (4, 10), (5, 40)],
        "parent_label": "organizer_name",
        "child_count_label": "total_events",
        "metric_total_label": "total_tickets",
    },
    {
        "key": "manufacturing",
        "title": "Manufacturing",
        "parent_table": "factories",
        "child_table": "machines",
        "event_table": "outputs",
        "parent_names": ["Plant A", "Plant B", "Plant C", "Plant D", "Plant E"],
        "child_label": "machine_name",
        "metric": "units_produced",
        "children": [(1, "Milling"), (1, "Press"), (2, "Lathe"), (3, "Cutter"), (4, "Welder")],
        "events": [(1, 100), (1, 80), (2, 60), (3, 25), (4, 140), (5, 15)],
        "parent_label": "factory_name",
        "child_count_label": "total_machines",
        "metric_total_label": "total_units_produced",
    },
    {
        "key": "recruiting",
        "title": "Recruiting",
        "parent_table": "recruiters",
        "child_table": "jobs",
        "event_table": "applications",
        "parent_names": ["Laura", "Mantas", "Greta", "Paulius", "Egle"],
        "child_label": "job_title",
        "metric": "application_count",
        "children": [(1, "Analyst"), (1, "Engineer"), (2, "Designer"), (3, "Manager"), (4, "Intern")],
        "events": [(1, 12), (1, 14), (2, 33), (3, 8), (4, 20), (5, 5)],
        "parent_label": "recruiter_name",
        "child_count_label": "total_jobs",
        "metric_total_label": "total_applications",
    },
]


for index, scenario in enumerate(SCENARIOS):
    scenario_setup = three_table_setup(
        scenario["parent_table"],
        scenario["child_table"],
        scenario["event_table"],
        scenario["parent_names"],
        scenario["child_label"],
        scenario["metric"],
        scenario["children"],
        scenario["events"],
    )
    SEED_TASKS.extend(
        scenario_tasks(
            key=scenario["key"],
            title=scenario["title"],
            setup_sql=scenario_setup,
            parent_table=scenario["parent_table"],
            child_table=scenario["child_table"],
            event_table=scenario["event_table"],
            child_label=scenario["child_label"],
            metric=scenario["metric"],
            parent_label=scenario["parent_label"],
            child_count_label=scenario["child_count_label"],
            metric_total_label=scenario["metric_total_label"],
            base_sort=1000 + index * 10,
        )
    )
