import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DongseoCrawler:
    def __init__(self, db_path='notices.db'):
        self.db_path = db_path
        self.base_url = "https://www.dongseo.ac.kr"
        self.notice_url = "https://www.dongseo.ac.kr/ko/board/notice"

        
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            # 스키마 파일 경로 설정
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            
            with sqlite3.connect(self.db_path) as conn:
                # 스키마 파일이 있으면 실행
                if os.path.exists(schema_path):
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema_sql = f.read()
                    conn.executescript(schema_sql)
                    logger.info("데이터베이스 스키마 초기화 완료")
                else:
                    # 스키마 파일이 없으면 기본 테이블 생성
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS notices (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            number TEXT,
                            title TEXT NOT NULL,
                            author TEXT,
                            date TEXT,
                            url TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS demo_notices (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            content TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    logger.info("기본 데이터베이스 테이블 생성 완료")
                    
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            
    def crawl_notices(self):
        """동서대학교 공지사항 크롤링"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.notice_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 공지사항 테이블 찾기 (수정된 선택자)
            notice_table = soup.find('table', class_='board-list-table')
            if not notice_table:
                # 대체 선택자 시도
                notice_table = soup.find('table', {'class': 'board_list'})
                if not notice_table:
                    notice_table = soup.find('div', class_='board_list')
                    
            if not notice_table:
                logger.warning("공지사항 테이블을 찾을 수 없습니다.")
                return []
                
            notices = []
            rows = notice_table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        # 번호 추출 (이미지가 있을 수 있음)
                        number_cell = cells[0]
                        number = number_cell.get_text(strip=True)
                        if not number or number in ['공지', 'Notice']:
                            number = '공지'
                            
                        # 제목 및 링크 추출
                        title_cell = cells[1]
                        title_link = title_cell.find('a')
                        if title_link:
                            title = title_link.get_text(strip=True)
                            href = title_link.get('href', '')
                            if href and not href.startswith('http'):
                                url = self.base_url + href
                            else:
                                url = href
                        else:
                            title = title_cell.get_text(strip=True)
                            url = ''
                            
                        # 작성자 추출
                        author = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        
                        # 날짜 추출
                        date = cells[3].get_text(strip=True) if len(cells) > 3 else ''
                        
                        if title:  # 제목이 있는 경우만 추가
                            notice = {
                                'number': number,
                                'title': title,
                                'author': author,
                                'date': date,
                                'url': url
                            }
                            notices.append(notice)
                            
                except Exception as e:
                    logger.warning(f"공지사항 파싱 오류: {e}")
                    continue
                    
            logger.info(f"크롤링 완료: {len(notices)}건의 공지사항")
            return notices
            
        except requests.RequestException as e:
            logger.error(f"웹사이트 접속 오류: {e}")
            return []
        except Exception as e:
            logger.error(f"크롤링 오류: {e}")
            return []
            
    def save_notices(self, notices):
        """공지사항을 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 기존 공지사항 삭제 (새로운 데이터로 갱신)
                conn.execute("DELETE FROM notices")
                
                # 새로운 공지사항 저장
                for notice in notices:
                    conn.execute('''
                        INSERT INTO notices (number, title, author, date, url)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        notice['number'],
                        notice['title'],
                        notice['author'],
                        notice['date'],
                        notice['url']
                    ))
                    
                conn.commit()
                logger.info(f"{len(notices)}건의 공지사항 저장 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 저장 오류: {e}")
            
    def get_notices(self, search_query=None, limit=50):
        """데이터베이스에서 공지사항 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if search_query:
                    cursor = conn.execute('''
                        SELECT * FROM notices 
                        WHERE title LIKE ? OR author LIKE ?
                        ORDER BY id DESC LIMIT ?
                    ''', (f'%{search_query}%', f'%{search_query}%', limit))
                else:
                    cursor = conn.execute('''
                        SELECT * FROM notices 
                        ORDER BY id DESC LIMIT ?
                    ''', (limit,))
                    
                notices = [dict(row) for row in cursor.fetchall()]
                return notices
                
        except Exception as e:
            logger.error(f"공지사항 조회 오류: {e}")
            return []
            
    def update_notices(self):
        """공지사항 업데이트 (크롤링 + 저장)"""
        notices = self.crawl_notices()
        if notices:
            self.save_notices(notices)
            return len(notices)
        return 0

