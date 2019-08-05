from setuptools import setup

setup(name='Expenses Tracker Backend',
      version='1.0.1',
      description='Backend for Expenses Tracker',
      url='https://github.com/kobonk/expenses_tracker',
      author='Kobonk',
      author_email='kobonk@kobonk.com',
      license='MIT',
      packages=['expense', 'rest', 'storage', 'tests'],
      zip_safe=False)
