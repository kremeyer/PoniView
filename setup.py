from setuptools import setup, find_packages

setup(
    name='PoniView',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/kremeyer/py_PoniView',
    license='',
    author='Laurenz Kremeyer',
    author_email='laurenz.kremeyer@mail.mcgill.ca',
    description='small gui application capable of loading diffraction images, alongside pyFAI poni files'
)
