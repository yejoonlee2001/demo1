-- 동서대학교 공지사항 데이터베이스 스키마
-- views 컬럼 제거하여 오류 해결

CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    title TEXT NOT NULL,
    author TEXT,
    date TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_notices_title ON notices(title);
CREATE INDEX IF NOT EXISTS idx_notices_date ON notices(date);
CREATE INDEX IF NOT EXISTS idx_notices_created_at ON notices(created_at);

-- 시연용 공지사항 테이블 (데모 기능용)
CREATE TABLE IF NOT EXISTS demo_notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

