"""
配置加载模块
从 .env 文件加载环境变量
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """配置类"""

    # 飞书应用配置
    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")

    # DeepSeek API 配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    # 临时文件目录
    TEMP_DIR = os.getenv("TEMP_DIR", "./temp")

    # 飞书域名
    FEISHU_DOMAIN = os.getenv("FEISHU_DOMAIN", "https://www.feishu.cn")

    @classmethod
    def validate(cls):
        """验证必需的配置项"""
        required = ["FEISHU_APP_ID", "FEISHU_APP_SECRET", "DEEPSEEK_API_KEY"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing)}")

    @classmethod
    def ensure_temp_dir(cls):
        """确保临时目录存在"""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)


# 导出配置实例
config = Config
