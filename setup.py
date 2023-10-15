from setuptools import setup, find_packages

setup(
    name="yxquant",
    version="0.1",
    description="yxquant",
    packages=find_packages(),
    package_data={
        'yxquant': ['dist/*'],
    },
    install_requires=[
        "pandas",
        "numpy",
        "backtrader",
        "requests"
    ],
    author="yzb",
    author_email="py.yangxiao@gmail.com",
    url="https://github.com/beautifulmonkey/yxquant",
)
