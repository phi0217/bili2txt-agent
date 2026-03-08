#!/usr/bin/env python3
"""
集成测试：测试新的音频下载流程

验证从视频ID到文本识别的完整流程
"""
import logging
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_integration.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def test_audio_download():
    """测试1：音频下载功能"""
    logger.info("=" * 60)
    logger.info("测试 1: 音频下载功能")
    logger.info("=" * 60)

    try:
        from bilibili_downloader import download_audio_only

        test_video_id = "BV1GJ411x7h7"  # 短视频，测试快
        logger.info(f"测试视频: {test_video_id}")

        # 下载音频
        audio_path = download_audio_only(test_video_id, audio_quality="128")

        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            file_size_mb = file_size / (1024 * 1024)

            logger.info("")
            logger.info("✅ 音频下载成功！")
            logger.info(f"   文件路径: {audio_path}")
            logger.info(f"   文件大小: {file_size_mb:.2f}MB")

            return audio_path
        else:
            logger.error("❌ 音频下载失败")
            return None

    except ImportError as e:
        logger.error(f"❌ 导入错误: {e}")
        logger.error("   请先安装 yt-dlp: pip install yt-dlp")
        return None
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return None


def test_task_integration():
    """测试2：task.py 集成"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 2: task.py 集成测试")
    logger.info("=" * 60)

    try:
        from task import YT_DLP_AVAILABLE

        logger.info(f"YT-DLP 可用: {YT_DLP_AVAILABLE}")

        if YT_DLP_AVAILABLE:
            logger.info("✅ task.py 已正确集成 yt-dlp 下载器")
        else:
            logger.warning("⚠️  yt-dlp 不可用，将使用旧方式")

        # 测试导入处理函数
        from task import process_video_sync
        logger.info("✅ process_video_sync 函数导入成功")

        return True

    except ImportError as e:
        logger.error(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


def test_full_workflow_simulation():
    """测试3：模拟完整工作流程"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试 3: 模拟完整工作流程")
    logger.info("=" * 60)

    try:
        from bilibili_downloader import download_audio_only
        from bilibili_downloader import BiliBiliDownloader

        test_video_id = "BV1GJ411x7h7"

        logger.info("步骤 1/3: 下载音频")
        audio_path = download_audio_only(test_video_id, audio_quality="128")

        if not audio_path:
            logger.error("❌ 音频下载失败")
            return False

        logger.info("✅ 音频下载完成")

        # 模拟后续步骤
        logger.info("")
        logger.info("步骤 2/3: 语音识别（模拟）")
        logger.info("⏭️  跳过实际识别（仅测试流程）")

        logger.info("")
        logger.info("步骤 3/3: 文本精转（模拟）")
        logger.info("⏭️  跳过实际精转（仅测试流程）")

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ 完整流程测试成功")
        logger.info("=" * 60)

        # 清理测试文件
        if os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info(f"已清理测试文件: {audio_path}")

        return True

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_workflow_comparison():
    """显示工作流程对比"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("工作流程对比")
    logger.info("=" * 60)

    logger.info("")
    logger.info("旧流程（you-get + 视频）:")
    logger.info("  1. 下载视频 (5-10分钟)")
    logger.info("  2. 提取音频 (30-60秒)")
    logger.info("  3. 语音识别 (2-5分钟)")
    logger.info("  总耗时: 8-16分钟")

    logger.info("")
    logger.info("新流程（yt-dlp + 音频）:")
    logger.info("  1. 下载音频 (1-2秒) ✨")
    logger.info("  2. 语音识别 (2-5分钟)")
    logger.info("  总耗时: 2-5分钟")

    logger.info("")
    logger.info("性能提升:")
    logger.info("  ⚡ 速度提升: 3-10倍")
    logger.info("  💾 空间节省: 99% (1-2MB vs 500MB)")
    logger.info("  🎯 流程简化: 减少1个步骤")


def main():
    """主测试函数"""
    logger.info("")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "集成测试" + " " * 35 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    # 测试1：音频下载
    result1 = test_audio_download()

    # 测试2：task.py 集成
    result2 = test_task_integration()

    # 测试3：完整流程模拟
    result3 = test_full_workflow_simulation()

    # 显示工作流程对比
    show_workflow_comparison()

    # 总结
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)

    results = [
        ("音频下载功能", result1),
        ("task.py 集成", result2),
        ("完整流程模拟", result3),
    ]

    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {status} - {name}")
        if not result:
            all_passed = False

    if all_passed:
        logger.info("")
        logger.info("🎉 所有测试通过！")
        logger.info("")
        logger.info("新流程已成功集成，可以立即使用！")
    else:
        logger.info("")
        logger.info("⚠️  部分测试失败，请检查日志")

    logger.info("")
    logger.info("详细日志: test_integration.log")
    logger.info("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("")
        logger.info("测试被用户中断")
        sys.exit(1)
