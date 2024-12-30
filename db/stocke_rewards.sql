CREATE TABLE IF NOT EXISTS stocke_rewards(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_name TEXT NOT NULL,
    announcement_title TEXT NOT NULL,
    pdf_url TEXT NOT NULL UNIQUE,
    has_reward BOOLEAN,
    ai_detection JSON,
    publish_date TEXT NOT NULL  -- 发布日期，文本类型
);