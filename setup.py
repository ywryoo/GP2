from setuptools import setup

setup(
    name='Graduation Project 2',
    long_description=__doc__,
    version='0.1.0',
    packages=['gp2-core'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
