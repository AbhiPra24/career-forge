from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="career-forge",
        version="0.1.0",
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        install_requires=[
            "rich>=13.0.0",
            "beautifulsoup4>=4.12.0",
            "python-dotenv>=1.0.0",
            "pypdf>=3.17.0",
        ],
        entry_points={
            "console_scripts": [
                "cforge = career_forge.cli:main",
                "career-forge = career_forge.cli:main",
            ],
        },
    )
