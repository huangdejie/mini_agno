"""模块 0 验收测试：确认开发环境就绪。

跑法：在项目根目录执行  uv run pytest
三个测试全绿 = 模块 0 通过，可以进入模块 1。
"""

import sys


def test_python_version():
    """Python 版本 >= 3.12（pyproject 里声明了，这里运行时再确认一次）。"""
    assert sys.version_info >= (3, 12), f"需要 Python >=3.12，当前是 {sys.version}"


def test_package_importable():
    """mini_agno 包能被正常导入、版本号就位。"""
    import mini_agno

    assert hasattr(mini_agno, "__version__")
    assert mini_agno.__version__ == "0.1.0"


def test_pydantic_available():
    """pydantic v2 可用 —— 模块 1 起会大量用到（agno 用它建模一切）。"""
    import pydantic

    assert pydantic.VERSION.startswith(
        "2"
    ), f"需要 pydantic v2，当前 {pydantic.VERSION}"
