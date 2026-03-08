#!/usr/bin/env python3
"""
B站视频实际下载测试
测试当前的 download_video 函数实际下载的清晰度
"""
import logging
import sys
import os
import subprocess

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_actual_download.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def test_current_implementation():
    """测试当前实现的下载行为"""
    logger.info("=" * 60)
    logger.info("测试当前 download_video 实现")
    logger.info("=" * 60)
    logger.info("")

    # 导入当前实现
    from bilibili_utils import download_video

    # 使用一个短视频进行测试
    test_video_id = "BV1GJ411x7h7"  # 短视频，测试快

    logger.info(f"测试视频: {test_video_id}")
    logger.info(f"视频链接: https://www.bilibili.com/video/{test_video_id}")
    logger.info("")

    try:
        logger.info("开始下载...")
        video_path = download_video(test_video_id)

        if video_path:
            logger.info("")
            logger.info("=" * 60)
            logger.info("下载成功！")
            logger.info("=" * 60)
            logger.info(f"文件路径: {video_path}")

            # 检查文件大小
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                file_size_mb = file_size / (1024 * 1024)

                logger.info(f"文件大小: {file_size_mb:.2f} MB ({file_size:,} bytes)")

                # 根据文件大小推测清晰度
                logger.info("")
                logger.info("清晰度推测（基于文件大小）:")

                if file_size_mb < 50:
                    logger.info("  ✓ 可能是 360p 或更低（理想情况）")
                elif file_size_mb < 100:
                    logger.info("  ✓ 可能是 480p")
                elif file_size_mb < 200:
                    logger.info("  ⚠ 可能是 720p")
                else:
                    logger.info("  ⚠ 可能是 1080p 或更高（清晰度过高）")

                # 获取文件信息
                logger.info("")
                logger.info("文件信息:")
                if os.name == 'nt':  # Windows
                    import json
                    # 使用 ffprobe 获取视频信息
                    try:
                        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                               '-show_format', '-show_streams', video_path]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            info = json.loads(result.stdout)
                            # 查找视频流
                            for stream in info.get('streams', []):
                                if stream.get('codec_type') == 'video':
                                    width = stream.get('width')
                                    height = stream.get('height')
                                    if width and height:
                                        logger.info(f"  分辨率: {width}x{height}")

                                        # 根据分辨率判断清晰度
                                        if height <= 360:
                                            logger.info("  ✓ 清晰度: 360p")
                                        elif height <= 480:
                                            logger.info("  ✓ 清晰度: 480p")
                                        elif height <= 720:
                                            logger.info("  ⚠ 清晰度: 720p")
                                        elif height <= 1080:
                                            logger.info("  ⚠ 清晰度: 1080p")
                                        break
                    except Exception as e:
                        logger.debug(f"无法获取视频信息: {e}")

            else:
                logger.warning(f"文件不存在: {video_path}")

        else:
            logger.error("")
            logger.error("=" * 60)
            logger.error("下载失败")
            logger.error("=" * 60)

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_manual_formats():
    """手动测试不同的格式参数"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("手动测试不同的 you-get 格式参数")
    logger.info("=" * 60)
    logger.info("")

    test_video_id = "BV1GJ411x7h7"
    test_url = f"https://www.bilibili.com/video/{test_video_id}"

    # 测试不同的格式
    formats_to_test = [
        ("不指定格式", []),
        ("360p", ["--format", "360p"]),
        ("480p", ["--format", "480p"]),
        ("flv360", ["--format", "flv360"]),
        ("flv480", ["--format", "flv480"]),
    ]

    results = {}

    for fmt_name, format_args in formats_to_test:
        logger.info(f"测试: {fmt_name}")

        cmd = ["you-get", "-i", test_url] + format_args
        logger.info(f"  命令: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            # 检查输出
            if "format" in result.stdout.lower():
                # 提取格式信息
                for line in result.stdout.split('\n'):
                    if 'format:' in line.lower() or 'quality:' in line.lower():
                        logger.info(f"  {line.strip()}")
                        break

            if result.returncode == 0:
                logger.info(f"  ✓ 成功")
                results[fmt_name] = "成功"
            else:
                if 'no such format' in result.stderr.lower():
                    logger.info(f"  ✗ 格式不存在")
                    results[fmt_name] = "格式不存在"
                elif 'you will need login' in result.stderr.lower():
                    logger.info(f"  ✗ 需要登录")
                    results[fmt_name] = "需要登录"
                else:
                    logger.info(f"  ✗ 失败: {result.stderr[:100]}")
                    results[fmt_name] = "失败"

        except subprocess.TimeoutExpired:
            logger.info(f"  ✗ 超时")
            results[fmt_name] = "超时"
        except Exception as e:
            logger.info(f"  ✗ 错误: {e}")
            results[fmt_name] = f"错误: {str(e)}"

        logger.info("")

    # 总结
    logger.info("=" * 60)
    logger.info("测试结果总结")
    logger.info("=" * 60)

    for fmt_name, result in results.items():
        status = "✓" if result == "成功" else "✗"
        logger.info(f"  {status} {fmt_name}: {result}")


def main():
    """主函数"""
    logger.info("")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "实际下载测试" + " " * 29 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    # 测试1：当前实现
    test_current_implementation()

    # 测试2：手动测试格式
    test_manual_formats()

    logger.info("")
    logger.info("=" * 60)
    logger.info("测试完成！")
    logger.info("详细日志已保存到: test_actual_download.log")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
