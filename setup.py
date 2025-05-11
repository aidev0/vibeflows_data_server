from setuptools import setup, find_packages

setup(
    name="data_server",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.0",
        "uvicorn==0.24.0",
        "pydantic==2.4.2",
        "python-dotenv==1.0.0",
        "motor==3.3.1",
        "pymongo==4.5.0",
        "gunicorn==21.2.0",
        "pydantic-settings==2.1.0",
        "python-multipart==0.0.9",
        "email-validator==2.1.0.post1",
        "dnspython==2.6.1"
    ],
    python_requires=">=3.11",
    author="VibeFlows",
    description="Data server for workflow automation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
) 