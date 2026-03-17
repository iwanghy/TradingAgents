"""
测试 html_to_jpg 模块功能

TDD Red Phase - 这些测试预期失败，因为功能代码尚未实现
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess


@pytest.fixture
def sample_html_path():
    """提供测试用的 HTML 文件路径"""
    return Path("tests/fixtures/sample_report.html")


@pytest.fixture
def output_dir(tmp_path):
    """提供临时输出目录"""
    return tmp_path / "output"


def test_convert_success(sample_html_path, output_dir):
    """测试成功的 HTML 到 JPG 转换"""
    # 导入待测试的模块（功能代码不存在时会导入失败）
    from tradingagents.utils import html_to_jpg

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 调用转换函数
    result = html_to_jpg.convert(
        html_path=sample_html_path,
        output_dir=output_dir,
        quality=85
    )

    # 验证返回值
    assert isinstance(result, list), "返回值应该是图片路径列表"
    assert len(result) > 0, "应该至少生成一张图片"

    # 验证生成的文件存在
    for img_path in result:
        assert Path(img_path).exists(), f"生成的图片文件应该存在: {img_path}"
        assert Path(img_path).suffix.lower() in ['.jpg', '.jpeg'], \
            f"生成的文件应该是 JPG 格式: {img_path}"


def test_missing_wkhtmltoimage(sample_html_path, output_dir):
    """测试 wkhtmltoimage 未安装的情况"""
    from tradingagents.utils import html_to_jpg

    output_dir.mkdir(parents=True, exist_ok=True)

    # Mock subprocess.run 来模拟 wkhtmltoimage 未安装
    with patch('subprocess.run', side_effect=FileNotFoundError("wkhtmltoimage not found")):
        with pytest.raises(FileNotFoundError, match="wkhtmltoimage"):
            html_to_jpg.convert(
                html_path=sample_html_path,
                output_dir=output_dir
            )


def test_file_not_found(output_dir):
    """测试 HTML 文件不存在的情况"""
    from tradingagents.utils import html_to_jpg

    output_dir.mkdir(parents=True, exist_ok=True)

    non_existent_path = Path("tests/fixtures/non_existent.html")

    with pytest.raises(FileNotFoundError, match="HTML file not found"):
        html_to_jpg.convert(
            html_path=non_existent_path,
            output_dir=output_dir
        )


def test_segmentation(sample_html_path, output_dir):
    """测试分段生成多张图片"""
    from tradingagents.utils import html_to_jpg

    output_dir.mkdir(parents=True, exist_ok=True)

    # 调用转换函数，启用分段
    result = html_to_jpg.convert(
        html_path=sample_html_path,
        output_dir=output_dir,
        enable_segmentation=True,
        max_segments=5
    )

    # 验证生成了多张图片（分段功能）
    assert len(result) > 1, "分段模式应该生成多张图片"

    # 验证所有文件都存在且为 JPG 格式
    for img_path in result:
        assert Path(img_path).exists(), f"生成的图片文件应该存在: {img_path}"
        assert Path(img_path).suffix.lower() in ['.jpg', '.jpeg'], \
            f"生成的文件应该是 JPG 格式: {img_path}"

    # 验证文件名有序号（分段命名）
    filenames = [Path(p).stem for p in result]
    # 应该包含类似 _page_0, _page_1 的模式
    assert any('_page_' in name for name in filenames), \
        "分段生成的文件应该包含页码标识"
