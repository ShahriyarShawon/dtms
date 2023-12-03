from setuptools import setup

setup(
    name='dtms',
    version='0.0.1',

    author='Shahriyar Shawon',
    author_email='ShahriyarShawon321@gmail.com',

    description='An api to reference drexel tms and course catalog data',

    url='https://github.com/ShahriyarShawon/dtms',

    packages=['dtms'],
    install_requires=[
        "beautifulsoup4",
        "yarl",
        "attrs",
        "requests",
        "click",
        "uvicorn",
        "sqlalchemy",
        "fastapi",
        "grequests",
        "gunicorn",
    ],

    entry_points={
        'console_scripts': [
        ],
    },

    python_requires='>=3.6',
)
