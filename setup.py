from setuptools import setup

setup(
    name='unicli',
    version='0.1',
    py_modules=['unicli'],
    include_package_data=True,
    install_requires=[
        'click', 'requests'
    ],
    entry_points='''
        [console_scripts]
        unicli=unicli:cli
    ''',
)
