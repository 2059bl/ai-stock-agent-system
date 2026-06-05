import time
import logging
import psycopg2
from typing import Dict, Any
import requests

class AgentSystem:
    def __init__(self):
        self.logger = self._setup_logger()
        self.is_running = False
        self.pg_connection = None
        self.ollama_api_url = os.getenv('OLLAMA_API_URL', 'http://ollama:11434')
        
    def _setup_logger(self):
        logger = logging.getLogger('AgentSystem')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def start(self):
        """啟動代理系統"""
        if self.is_running:
            self.logger.warning("代理系統已經在運行中")
            return
            
        self.logger.info("正在啟動 Agent System...")
        self.is_running = True
        
        # 初始化資料庫連接
        self._initialize_database()
        
        # 初始化 Ollama 連接
        self._initialize_ollama()
        
        self.logger.info("Agent System 啟動完成")
    
    def _initialize_database(self):
        """初始化 PostgreSQL 連接"""
        pg_connection_string = os.getenv('PG_CONNECTION_STRING')
        if not pg_connection_string:
            self.logger.warning("未配置 PostgreSQL 連接字串")
            return
            
        try:
            self.pg_connection = psycopg2.connect(pg_connection_string)
            self.logger.info("PostgreSQL 連接成功")
        except Exception as e:
            self.logger.error(f"PostgreSQL 連接失敗: {e}")
            raise
    
    def _initialize_ollama(self):
        """初始化 Ollama 連接"""
        try:
            # 測試 Ollama 連接
            response = requests.get(f"{self.ollama_api_url}/api/tags")
            if response.status_code == 200:
                self.logger.info("Ollama 連接成功")
            else:
                self.logger.error(f"Ollama 連接失敗: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Ollama 連接測試失敗: {e}")
    
    def process_stock_data(self, stock_symbol: str) -> Dict[str, Any]:
        """處理股票數據"""
        if not self.is_running:
            return {"status": "error", "message": "代理系統未運行"}
            
        try:
            # 從資料庫獲取股票數據
            stock_data = self._get_stock_data_from_db(stock_symbol)
            
            # 使用 Ollama 分析數據
            analysis = self._analyze_with_ollama(stock_data)
            
            return {
                "status": "success",
                "stock_data": stock_data,
                "analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"處理股票數據時發生錯誤: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_stock_data_from_db(self, stock_symbol: str) -> Dict[str, Any]:
        """從 PostgreSQL 獲取股票數據"""
        if not self.pg_connection:
            raise Exception("PostgreSQL 連接未初始化")
            
        try:
            cursor = self.pg_connection.cursor()
            cursor.execute(
                "SELECT * FROM stock_data WHERE symbol = %s ORDER BY timestamp DESC LIMIT 1",
                (stock_symbol,)
            )
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    "symbol": stock_symbol,
                    "price": result[1],
                    "timestamp": result[2].isoformat()
                }
            else:
                raise Exception(f"未找到股票 {stock_symbol} 的數據")
                
        except Exception as e:
            self.logger.error(f"從資料庫獲取數據失敗: {e}")
            raise
    
    def _analyze_with_ollama(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Ollama 分析股票數據"""
        try:
            prompt = f"""
            分析以下股票數據：
            股票代碼: {stock_data['symbol']}
            價格: {stock_data['price']}
            時間: {stock_data['timestamp']}
            
            請提供：
            1. 趨勢分析
            2. 投資建議
            3. 風險評估
            """
            
            response = requests.post(
                f"{self.ollama_api_url}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "analysis": response.json().get('response', ''),
                    "model": 'llama3'
                }
            else:
                raise Exception(f"Ollama 分析失敗: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Ollama 分析失敗: {e}")
            raise
    
    def stop(self):
        """停止代理系統"""
        if not self.is_running:
            self.logger.warning("代理系統已經停止")
            return
            
        self.logger.info("正在停止 Agent System...")
        self.is_running = False
        
        # 關閉資料庫連接
        if self.pg_connection:
            self.pg_connection.close()
            self.logger.info("PostgreSQL 連接已關閉")
        
        self.logger.info("Agent System 已停止")
