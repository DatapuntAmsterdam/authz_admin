""" See <https://setuptools.readthedocs.io/en/latest/>.
"""
from setuptools import setup


setup(
    version='0.1.1',
    name='datapunt-oauth2',
    description="Permission Management and OAuth2 Authorization Service",
    # long_description="",
    url='https://github.com/DatapuntAmsterdam/oauth2',
    author='Amsterdam Datapunt',
    author_email='datapunt.ois@amsterdam.nl',
    license='Mozilla Public License Version 2.0',
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['oauth2'],
    install_requires=[
        'jsonschema',
        'psycopg2',
        'pyyaml',
        'sqlalchemy',
        'aiohttp==2.0.7'
    ],
    extras_require={
        'doc': [
            'sphinx',
            'sphinx_rtd_theme'
        ],
        'dev': [
            'pytest==3.0.5',
            'pytest-cov==2.4.0'
        ],
    },
    entry_points={
        'console_scripts': [
            'authorization_service = oauth2.authorization_service.server:start',
            'client_admin_service = oauth2.client_admin_service.server:start',
            'scope_admin_service = oauth2.scope_admin_service.main:start',
        ],
    },
)
