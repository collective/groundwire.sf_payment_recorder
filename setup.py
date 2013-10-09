from setuptools import setup, find_packages

version = '2.0'

setup(name='groundwire.sf_payment_recorder',
      version=version,
      description="Records GetPaid orders in Salesforce via the GW_Online_Payment web service.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='salesforce suds soap zope plone',
      author='David Glick, Groundwire',
      author_email='davidglick@groundwire.org',
      url='https://groundwire.devguard.com/svn/public/groundwire.sf_payment_recorder/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['groundwire'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plone.app.registry',
          'collective.salesforce.credentials',
          'getpaid.core>=0.9.1',
          'setuptools',
          'suds',
          'z3c.suds',
          'zope.component',
          'zope.interface',
          'zope.schema',
          # -*- Extra requirements: -*-
      ],
      )
