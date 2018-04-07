from setuptools import setup 


setup(name="gaze",
        version='0.1',
        description='simple server for viewing source code files',
        url='no url yet',
        author='Kolten Pearson',
        author_email='koltenpearson@gmail.com',
        license='INTERNAL USE ONLY',
        packages=['gaze'],
        scripts=['bin/gaze'],
        include_package_data=True,
        install_requires=[
            'pygments',
            'pygments-style-solarized',
            'cherrypy',
        ]
        zip_safe=False)

