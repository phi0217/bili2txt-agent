#!/usr/bin/env python3
"""
you-get 连接诊断工具
诊断 you-get 是否能正常访问B站
"""
import subprocess
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def check_you_get_version():
    """检查 you-get 版本"""
    print("=" * 60)
    print("检查 you-get 版本")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["you-get", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"✓ you-get 已安装")
            print(f"  版本: {result.stdout.strip()}")
        else:
            print(f"✗ you-get 未正确安装")
            return False
    except FileNotFoundError:
        print(f"✗ you-get 未找到")
        print(f"  请安装: pip install you-get")
        return False
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

    return True

def check_network_connection():
    """检查网络连接"""
    print("\n" + "=" * 60)
    print("检查网络连接")
    print("=" * 60)

    test_url = "https://www.bilibili.com"

    try:
        import requests
        print(f"尝试连接: {test_url}")

        response = requests.get(test_url, timeout=10)

        if response.status_code == 200:
            print(f"✓ 网络连接正常")
            print(f"  状态码: {response.status_code}")
        else:
            print(f"⚠ 连接成功但状态异常: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"✗ 连接超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ 连接失败")
        print(f"  可能需要代理")
        return False
    except Exception as e:
        print(f"✗ 网络错误: {e}")
        return False

    return True

def test_you_get_simple():
    """简单测试 you-get"""
    print("\n" + "=" * 60)
    print("测试 you-get 基本功能")
    print("=" * 60)

    # 使用一个简单的命令
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"

    print(f"测试URL: {test_url}")
    print("\n尝试获取视频信息（不下载）...")

    try:
        # 使用 --info 参数，只获取信息不下载
        cmd = ["you-get", "-i", test_url]
        print(f"命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 增加超时时间到60秒
        )

        print("\n" + "-" * 60)
        print("返回码:", result.returncode)

        if result.stdout:
            print("\n标准输出（前500字符）:")
            print(result.stdout[:500])

        if result.stderr:
            print("\n标准错误（前500字符）:")
            print(result.stderr[:500])

        print("-" * 60)

        if result.returncode == 0:
            print("\n✓ you-get 工作正常")
            return True
        else:
            print("\n✗ you-get 返回错误")
            return False

    except subprocess.TimeoutExpired:
        print("\n✗ 命令执行超时")
        print("  可能原因:")
        print("  1. 网络连接慢")
        print("  2. 需要代理")
        print("  3. B站访问限制")
        return False
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        return False

def check_proxy_settings():
    """检查代理设置"""
    print("\n" + "=" * 60)
    print("检查代理设置")
    print("=" * 60)

    import os

    proxies = {
        'HTTP_PROXY': os.environ.get('HTTP_PROXY'),
        'HTTPS_PROXY': os.environ.get('HTTPS_PROXY'),
        'http_proxy': os.environ.get('http_proxy'),
        'https_proxy': os.environ.get('https_proxy'),
    }

    has_proxy = False
    for key, value in proxies.items():
        if value:
            print(f"✓ {key}={value}")
            has_proxy = True

    if not has_proxy:
        print("未设置代理")
        print("\n如果需要代理，请设置:")
        print("  Windows PowerShell:")
        print("    $env:HTTP_PROXY='http://127.0.0.1:7890'")
        print("    $env:HTTPS_PROXY='http://127.0.0.1:7890'")
        print("\n  或在 .env 文件中添加:")
        print("    HTTP_PROXY=http://127.0.0.1:7890")
        print("    HTTPS_PROXY=http://127.0.0.1:7890")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n" + "=" * 60)
    print("解决方案建议")
    print("=" * 60)

    print("\n如果 you-get 无法访问B站，可以尝试:")

    print("\n方案1: 配置代理")
    print("  如果你使用代理访问B站:")
    print("  1. 设置环境变量 HTTP_PROXY 和 HTTPS_PROXY")
    print("  2. 或在 you-get 命令中使用 --http-proxy 参数")

    print("\n方案2: 使用 yt-dlp 替代")
    print("  yt-dlp 是更现代的视频下载工具:")
    print("  1. 安装: pip install yt-dlp")
    print("  2. 使用: yt-dlp -f 'bestvideo[height<=360]+bestaudio' URL")

    print("\n方案3: 更新 you-get")
    print("  pip install --upgrade you-get")

    print("\n方案4: 使用B站API")
    print("  直接调用B站API获取视频信息")
    print("  可以避免 you-get 的网络问题")

def main():
    """主函数"""
    print("\n╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "you-get 诊断工具" + " " * 28 + "║")
    print("╚" + "=" * 58 + "╝\n")

    # 检查列表
    checks = []

    # 1. 检查版本
    checks.append(("you-get 版本", check_you_get_version))

    # 2. 检查网络
    checks.append(("网络连接", check_network_connection))

    # 3. 检查代理
    check_proxy_settings()

    # 4. 测试 you-get
    checks.append(("you-get 功能", test_you_get_simple))

    # 显示结果
    print("\n" + "=" * 60)
    print("诊断结果汇总")
    print("=" * 60)

    for name, result in checks:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status} - {name}")

    # 提供建议
    all_passed = all(result for _, result in checks)

    if not all_passed:
        suggest_solutions()
    else:
        print("\n✓ 所有检查通过！you-get 工作正常。")
        print("\n如果下载视频仍然超时，可能是因为:")
        print("  1. 视频较大，下载时间较长")
        print("  2. B站对you-get的限制")
        print("  3. 网络速度较慢")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
        sys.exit(1)
