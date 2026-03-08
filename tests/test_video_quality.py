#!/usr/bin/env python3
"""
B站视频清晰度下载测试
探索如何下载不同清晰度的B站视频，找出最低可用清晰度
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
        logging.FileHandler('test_video_quality.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BiliBiliVideoQualityTester:
    """B站视频清晰度测试类"""

    def __init__(self):
        """初始化测试器"""
        self.test_video_id = "BV1GJ411x7h7"  # 一个测试用的视频ID
        self.test_url = f"https://www.bilibili.com/video/{self.test_video_id}"
        self.temp_dir = "./temp"
        self.results = []

    def test_format_detection(self) -> Dict[str, any]:
        """测试1：检测视频支持的格式"""
        logger.info("=" * 60)
        logger.info("测试 1: 检测视频支持的格式")
        logger.info("=" * 60)

        try:
            # 使用 you-get --info 查看视频信息
            cmd = ["you-get", "--info", self.test_url]
            logger.info(f"执行命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            logger.info("-" * 60)
            logger.info("STDOUT:")
            logger.info(result.stdout)

            if result.stderr:
                logger.info("-" * 60)
                logger.info("STDERR:")
                logger.info(result.stderr)

            logger.info("-" * 60)

            # 解析输出，查找可用格式
            formats = self._parse_formats(result.stdout)

            logger.info(f"检测到 {len(formats)} 种格式:")
            for fmt in formats:
                logger.info(f"  - {fmt}")

            return {
                "success": result.returncode == 0,
                "formats": formats,
                "output": result.stdout
            }

        except subprocess.TimeoutExpired:
            logger.error("命令执行超时")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.error(f"执行失败: {e}")
            return {"success": False, "error": str(e)}

    def _parse_formats(self, output: str) -> List[str]:
        """从you-get输出中解析可用格式"""
        formats = []
        lines = output.split('\n')

        for line in lines:
            # 查找包含格式信息的行
            # you-get通常输出格式信息，如:
            # - format:        dash-flv720
            # - format:        dash-flv480
            # - format:        MP4
            if 'format:' in line.lower():
                formats.append(line.strip())
            elif 'quality:' in line.lower():
                formats.append(line.strip())

        return formats

    def test_specific_format(self, format_value: str) -> Dict[str, any]:
        """测试2：下载指定格式"""
        logger.info("=" * 60)
        logger.info(f"测试 2: 尝试下载格式 '{format_value}'")
        logger.info("=" * 60)

        try:
            # 构建下载命令
            cmd = ["you-get", "-o", self.temp_dir, "--format", format_value, self.test_url]
            logger.info(f"执行命令: {' '.join(cmd)}")

            # 只显示下载信息，不实际下载完整文件
            # 使用 --json 参数获取信息
            info_cmd = ["you-get", "--json", "--format", format_value, self.test_url]
            logger.info(f"信息命令: {' '.join(info_cmd)}")

            result = subprocess.run(
                info_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            logger.info("-" * 60)
            logger.info("STDOUT:")
            logger.info(result.stdout[:500])  # 只显示前500字符

            if result.stderr:
                logger.info("-" * 60)
                logger.info("STDERR:")
                logger.info(result.stderr[:500])

            # 判断是否成功
            success = result.returncode == 0
            error = None

            if not success:
                error = result.stderr[:200] if result.stderr else "未知错误"

                # 检查特定错误
                if 'no such format' in error.lower():
                    error = "格式不存在"
                elif 'you will need login' in error.lower():
                    error = "需要登录"
                elif 'format not found' in error.lower():
                    error = "格式未找到"

            logger.info("-" * 60)
            if success:
                logger.info(f"✓ 格式 '{format_value}' 可用")
            else:
                logger.warning(f"✗ 格式 '{format_value}' 不可用: {error}")

            return {
                "format": format_value,
                "success": success,
                "error": error
            }

        except subprocess.TimeoutExpired:
            logger.error(f"格式 '{format_value}' 测试超时")
            return {"format": format_value, "success": False, "error": "timeout"}
        except Exception as e:
            logger.error(f"格式 '{format_value}' 测试失败: {e}")
            return {"format": format_value, "success": False, "error": str(e)}

    def test_multiple_formats(self) -> List[Dict[str, any]]:
        """测试3：批量测试多个格式"""
        logger.info("=" * 60)
        logger.info("测试 3: 批量测试多个格式")
        logger.info("=" * 60)

        # B站常见的格式列表
        # 参考：https://github.com/soimort/you-get/wiki/Bilibili
        test_formats = [
            # 尝试不同的格式名称
            "360p",
            "480p",
            "720p",
            "1080p",
            "flv720",
            "flv480",
            "flv360",
            "mp4",
            "dash-flv720",
            "dash-flv480",
            "dash-flv360",
            "dash-mp4720",
            "dash-mp4480",
            "dash-mp4360",
            # 你-get 使用的格式ID
            "16",  # 流畅 360P
            "32",  # 清晰 480P
            "64",  # 高清 720P
            "80",  # 高清 1080P
        ]

        results = []

        for fmt in test_formats:
            result = self.test_specific_format(fmt)
            results.append(result)

            # 短暂延迟，避免请求过快
            import time
            time.sleep(1)

        return results

    def analyze_results(self, results: List[Dict[str, any]]) -> None:
        """分析测试结果"""
        logger.info("=" * 60)
        logger.info("测试结果分析")
        logger.info("=" * 60)

        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]

        logger.info(f"总测试格式数: {len(results)}")
        logger.info(f"成功: {len(successful)}")
        logger.info(f"失败: {len(failed)}")

        logger.info("")
        logger.info("成功的格式:")
        for r in successful:
            logger.info(f"  ✓ {r['format']}")

        logger.info("")
        logger.info("失败的格式:")
        for r in failed:
            error = r.get('error', '未知错误')
            logger.info(f"  ✗ {r['format']} - {error}")

        logger.info("")
        logger.info("推荐策略:")

        if successful:
            # 找到最低的可用格式
            lowest = self._find_lowest_quality(successful)
            logger.info(f"  建议使用格式: {lowest}")
            logger.info("  这是在测试中成功的最低清晰度格式")
        else:
            logger.warning("  没有找到成功的格式")
            logger.warning("  建议：")
            logger.warning("    1. 不使用 --format 参数，让 you-get 选择默认格式")
            logger.warning("    2. 或者配置 B站 cookies 来访问更多格式")

    def _find_lowest_quality(self, successful: List[Dict[str, any]]) -> Optional[str]:
        """从成功格式中找出最低清晰度"""
        # 按优先级排序
        quality_order = [
            "360", "flv360", "dash-flv360", "dash-mp4360",
            "480", "flv480", "dash-flv480", "dash-mp4480",
            "720", "flv720", "dash-flv720", "dash-mp4720",
            "1080"
        ]

        for q in quality_order:
            for r in successful:
                if q in r['format']:
                    return r['format']

        # 如果没有匹配，返回第一个成功的
        return successful[0]['format'] if successful else None

    def run_full_test(self):
        """运行完整测试流程"""
        logger.info("")
        logger.info("╔" + "=" * 58 + "╗")
        logger.info("║" + " " * 10 + "B站视频清晰度测试" + " " * 30 + "║")
        logger.info("╚" + "=" * 58 + "╝")
        logger.info("")

        # 测试1：检测可用格式
        format_info = self.test_format_detection()
        logger.info("")

        # 测试2-3：测试多个格式
        results = self.test_multiple_formats()
        logger.info("")

        # 分析结果
        self.analyze_results(results)
        logger.info("")

        # 生成建议
        logger.info("=" * 60)
        logger.info("实现建议")
        logger.info("=" * 60)

        successful = [r for r in results if r.get("success", False)]

        if successful:
            logger.info("")
            logger.info("✓ 找到可用的低清晰度格式！")
            logger.info("")
            logger.info("推荐实现方式:")
            logger.info("```python")
            logger.info("# bilibili_utils.py 中的 download_video 函数")

            lowest = self._find_lowest_quality(successful)
            logger.info(f"def download_video(video_id: str, format: str = '{lowest}'):")

            logger.info("```")
            logger.info("")
            logger.info(f"建议将默认格式设置为: {lowest}")
        else:
            logger.info("")
            logger.info("✗ 所有指定格式都失败")
            logger.info("")
            logger.info("替代方案:")
            logger.info("1. 不指定格式，让 you-get 自动选择:")
            logger.info("```python")
            logger.info("cmd = ['you-get', '-o', temp_dir, video_url]")
            logger.info("```")
            logger.info("")
            logger.info("2. 使用 cookies 访问更多格式:")
            logger.info("```python")
            logger.info("cmd = ['you-get', '-o', temp_dir, '--cookies', 'cookies.txt', video_url]")
            logger.info("```")


def main():
    """主测试函数"""
    tester = BiliBiliVideoQualityTester()

    try:
        tester.run_full_test()
        logger.info("")
        logger.info("=" * 60)
        logger.info("测试完成！")
        logger.info("详细日志已保存到: test_video_quality.log")
        logger.info("=" * 60)
        return 0

    except KeyboardInterrupt:
        logger.info("")
        logger.info("测试被用户中断")
        return 1
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
