import os
import sys
import logging
import requests
from agent_system import AgentSystem
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class StockAIAgent:
    def __init__(self):
        self.logger = self._setup_logger()
        self.agent_system = AgentSystem()
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL')
        self.ollama_api_url = os.getenv('OLLAMA_API_URL', 'http://ollama:11434')
        self.pg_connection_string = os.getenv('PG_CONNECTION_STRING')
        
    def _setup_logger(self):
        """設置日誌記錄器"""
        logger = logging.getLogger('StockAIAgent')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def start(self):
        """啟動代理系統"""
        try:
            self.logger.info("正在啟動 Stock AI Agent...")
            self.agent_system.start()
            self.logger.info("Stock AI Agent 啟動完成")
            
            # 觸發 n8n 工作流
            self.trigger_n8n_workflow()
            
        except Exception as e:
            self.logger.error(f"啟動失敗: {e}")
            sys.exit(1)
    
    def trigger_n8n_workflow(self):
        """觸發 n8n 工作流"""
        if not self.n8n_webhook_url:
            self.logger.warning("未配置 n8n webhook URL")
            return
            
        try:
            payload = {
                "event": "agent_started",
                "service": "stock-ai-agent",
                "timestamp": time.time()
            }
            
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("n8n 工作流觸發成功")
            else:
                self.logger.error(f"n8n 工作流觸發失敗: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"觸發 n8n 工作流時發生錯誤: {e}")

def main():
    agent = StockAIAgent()
    agent.start()

if __name__ == "__main__":
    main()
