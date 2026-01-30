"""
AICloud-Innovation Enterprise Framework
Setup configuration for package installation
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aicloud-innovation",
    version="1.0.0",
    author="AICloud Innovation Team",
    author_email="info@aicloud-innovation.com",
    description="Enterprise-level framework for developing powerful AI Agentic Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "aws": [
            "boto3>=1.28.0",
            "botocore>=1.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aicloud-demo=examples.enterprise_framework_demo:main",
        ],
    },
    include_package_data=True,
    keywords="ai agents healthcare enterprise medical diagnosis treatment monitoring",
    project_urls={
        "Bug Reports": "https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent/issues",
        "Documentation": "https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent/blob/main/AICLOUD_INNOVATION_FRAMEWORK.md",
        "Source": "https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent",
    },
)
