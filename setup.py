from setuptools import setup, find_packages

setup(
    name="GraphPlotYT",
    version="0.1",
    packages=find_packages(),
    description="Plot backtest graph",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Gary YT Lau",
    author_email="lauytgary@gmail.com",
    url="https://github.com/lauytgary/GraphPlotYT",
    install_requires=['pandas>=1.5.0', 'plotly>= 5.10.0,< 6'],  # 列出依赖项
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)