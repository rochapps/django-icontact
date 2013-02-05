from distutils.core import setup
setup(
    name = "django-icontact",
    packages = ["icontact", ],
    version = "0.3.0",
    description = "A Django application allowing developers to synchronise instances of their models with iContact.",
    author = "RochApps, LLC",
    author_email = "info@rochapps.com",
    url = "http://rochapps.com/",
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
