#!/usr/bin/env python3
"""
yt-dlp 视频下载测试
测试 yt-dlp 是否能正常工作，并测试不同的清晰度选项
"""
import logging
import sys
import os
import subprocess
from typing import List, Dict, Optional

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_yt_dlp.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class YtDlpVideoQualityTester:
    """yt-dlp 视频清晰度测试类"""

    def __init__(self):
        """初始化测试器"""
        self.test_video_id = "BV1GJ411x7h7"
        self.test_url = f"https://www.bilibili.com/video/{self.test_video_id}"
        self.temp_dir = "./temp"
        self.results = []

    def check_yt_dlp_installed(self) -> bool:
        """检查 yt-dlp 是否已安装"""
        logger.info("=" * 60)
        logger.info("检查 yt-dlp 安装")
        logger.info("=" * 60)

        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"✓ yt-dlp 已安装")
                logger.info(f"  版本: {result.stdout.strip()}")
                return True
            else:
                logger.error("✗ yt-dlp 未正确安装")
                return False

        except FileNotFoundError:
            logger.error("✗ yt-dlp 未找到")
            logger.error("  请安装: pip install yt-dlp")
            return False
        except Exception as e:
            logger.error(f"✗ 检查失败: {e}")
            return False

    def test_list_formats(self) -> List[str]:
        """测试1：列出可用格式"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试 1: 列出可用格式")
        logger.info("=" * 60)

        try:
            cmd = ["yt-dlp", "--list-formats", self.test_url]
            logger.info(f"执行命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )

            logger.info("-" * 60)
            logger.info("输出（前1000字符）:")
            logger.info(result.stdout[:1000])
            logger.info("-" * 60)

            if result.returncode == 0:
                logger.info("✓ 成功获取格式列表")
                return self._parse_formats(result.stdout)
            else:
                logger.error("✗ 获取格式列表失败")
                if result.stderr:
                    logger.error(f"错误: {result.stderr[:500]}")
                return []

        except subprocess.TimeoutExpired:
            logger.error("✗ 命令执行超时")
            return []
        except Exception as e:
            logger.error(f"✗ 执行失败: {e}")
            return []

    def _parse_formats(self, output: str) -> List[str]:
        """从输出中解析格式信息"""
        formats = []
        lines = output.split('\n')

        for line in lines:
            # 查找包含格式代码的行
            # yt-dlp 输出格式如:
            # 360p | 64   | mp4  | 640x360   | 64   | video only
            if 'p |' in line or 'dash' in line:
                formats.append(line.strip())

        return formats

    def test_format_download(self, format_spec: str, description: str) -> Dict[str, any]:
        """测试2：测试特定格式"""
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"测试格式: {description}")
        logger.info("=" * 60)

        try:
            # 使用 --print 获取输出文件名，不实际下载
            cmd = [
                "yt-dlp",
                "-f", format_spec,
                "--print", "filename",
                "-o", f"{self.temp_dir}/test_download.%(ext)s",
                self.test_url
            ]

            logger.info(f"格式: {format_spec}")
            logger.info(f"命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )

            logger.info("-" * 60)

            if result.returncode == 0:
                logger.info(f"✓ 格式 '{description}' 可用")
                logger.info(f"  输出文件: {result.stdout.strip()}")
                return {
                    "format": format_spec,
                    "description": description,
                    "success": True,
                    "filename": result.stdout.strip()
                }
            else:
                error_msg = result.stderr[:200] if result.stderr else "未知错误"

                if 'no suitable format' in error_msg.lower():
                    error_msg = "无合适格式"
                elif 'video not found' in error_msg.lower():
                    error_msg = "视频未找到"

                logger.warning(f"✗ 格式 '{description}' 不可用: {error_msg}")
                return {
                    "format": format_spec,
                    "description": description,
                    "success": False,
                    "error": error_msg
                }

        except subprocess.TimeoutExpired:
            logger.error(f"✗ 格式 '{description}' 测试超时")
            return {
                "format": format_spec,
                "description": description,
                "success": False,
                "error": "超时"
            }
        except Exception as e:
            logger.error(f"✗ 格式 '{description}' 测试失败: {e}")
            return {
                "format": format_spec,
                "description": description,
                "success": False,
                "error": str(e)
            }

    def test_audio_only(self) -> Dict[str, any]:
        """测试3：只下载音频（推荐）"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试: 只下载音频（推荐用于语音识别）")
        logger.info("=" * 60)

        try:
            cmd = [
                "yt-dlp",
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "128K",  # 128kbps 足够识别
                "--print", "filename",
                "-o", f"{self.temp_dir}/test_audio.%(ext)s",
                self.test_url
            ]

            logger.info(f"命令: {' '.join(cmd)}")
            logger.info("说明: 只下载音频，跳过视频")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )

            logger.info("-" * 60)

            if result.returncode == 0:
                logger.info("✓ 音频下载功能可用")
                logger.info(f"  输出文件: {result.stdout.strip()}")
                return {
                    "success": True,
                    "filename": result.stdout.strip()
                }
            else:
                logger.error("✗ 音频下载失败")
                if result.stderr:
                    logger.error(f"  错误: {result.stderr[:500]}")
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            logger.error("✗ 音频下载测试超时")
            return {"success": False, "error": "超时"}
        except Exception as e:
            logger.error(f"✗ 测试失败: {e}")
            return {"success": False, "error": str(e)}

    def analyze_results(self, video_results: List[Dict], audio_result: Dict):
        """分析测试结果"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试结果分析")
        logger.info("=" * 60)

        # 视频格式结果
        successful = [r for r in video_results if r.get("success", False)]
        failed = [r for r in video_results if not r.get("success", False)]

        logger.info(f"视频格式测试:")
        logger.info(f"  总数: {len(video_results)}")
        logger.info(f"  成功: {len(successful)}")
        logger.info(f"  失败: {len(failed)}")

        if successful:
            logger.info("")
            logger.info("成功的格式:")
            for r in successful:
                logger.info(f"  ✓ {r['description']}")

        if failed:
            logger.info("")
            logger.info("失败的格式:")
            for r in failed:
                error = r.get('error', '未知错误')
                logger.info(f"  ✗ {r['description']} - {error}")

        # 音频下载结果
        logger.info("")
        logger.info(f"音频下载测试:")
        if audio_result.get("success", False):
            logger.info("  ✓ 可用")
        else:
            logger.info(f"  ✗ 不可用: {audio_result.get('error', '未知错误')}")

        # 推荐
        logger.info("")
        logger.info("=" * 60)
        logger.info("推荐策略")
        logger.info("=" * 60)

        if audio_result.get("success", False):
            logger.info("")
            logger.info("✓✓✓ 强烈推荐：只下载音频")
            logger.info("")
            logger.info("对于语音识别项目，只下载音频是最佳选择:")
            logger.info("  ✓ 速度最快（跳过视频）")
            logger.info("  ✓ 文件最小（约5-10MB）")
            logger.info("  ✓ 音频质量足够（128K MP3）")
            logger.info("  ✓ 无需后续提取")
            logger.info("")
            logger.info("实现代码:")
            logger.info("```python")
            logger.info("import yt_dlp")
            logger.info("")
            logger.info("def download_audio(video_id: str):")
            logger.info('    ydl_opts = {')
            logger.info("        'format': 'bestaudio',")
            logger.info("        'postprocessors': [{")
            logger.info("            'key': 'FFmpegExtractAudio',")
            logger.info("            'preferredcodec': 'mp3',")
            logger.info("            'preferredquality': '128',")
            logger.info("        }],")
            logger.info("    }")
            logger.info("")
            logger.info("    with yt_dlp.YoutubeDL(ydl_opts) as ydl:")
            logger.info("        info = ydl.extract_info(url, download=True)")
            logger.info("        return ydl.prepare_filename(info)")
            logger.info("```")

        elif successful:
            logger.info("")
            logger.info("✓ 推荐：下载最低清晰度视频")

            # 找最低清晰度
            lowest = successful[0]
            logger.info(f"  格式: {lowest['description']}")
            logger.info(f"  规格: {lowest['format']}")

        else:
            logger.warning("")
            logger.warning("✗ 所有格式都失败")
            logger.warning("  可能需要:")
            logger.warning("    1. 配置代理")
            logger.warning("    2. 使用cookies")
            logger.warning("    3. 检查网络连接")

    def run_full_test(self):
        """运行完整测试"""
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 18 + "yt-dlp 测试" + " " * 30 + "║")
        logger.info("╚" + "=" * 58 + "╝")
        logger.info("")

        # 检查安装
        if not self.check_yt_dlp_installed():
            logger.error("")
            logger.error("yt-dlp 未安装，请先安装:")
            logger.error("  pip install yt-dlp")
            return

        # 测试1：列出格式
        formats = self.test_list_formats()
        logger.info("")

        # 测试2：不同视频格式
        video_tests = [
            ("worst", "最低质量（推荐）"),
            ("worstvideo[height<=480]+bestaudio", "最高480p"),
            ("bestvideo[height<=360]+bestaudio", "360p"),
            ("bestvideo[height<=720]+bestaudio", "720p"),
        ]

        video_results = []
        for format_spec, description in video_tests:
            result = self.test_format_download(format_spec, description)
            video_results.append(result)

        # 测试3：只下载音频
        audio_result = self.test_audio_only()

        # 分析结果
        self.analyze_results(video_results, audio_result)

        logger.info("")
        logger.info("=" * 60)
        logger.info("测试完成！")
        logger.info("详细日志: test_yt_dlp.log")
        logger.info("=" * 60)


def main():
    """主函数"""
    tester = YtDlpVideoQualityTester()

    try:
        tester.run_full_test()
        return 0
    except KeyboardInterrupt:
        logger.info("")
        logger.info("测试被用户中断")
        return 1
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
