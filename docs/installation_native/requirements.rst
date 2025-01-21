Requirements
============

* A (virtual) server to install BYCEPS on
* At least two subdomains (administration UI, one party website)
* An SMTP_ server (to send emails)
* Software:

  * Python_ 3.11 or higher
  * PostgreSQL_ 13 or higher (for data persistence)
  * Redis_ 5.0 or higher (for the background job queue)
  * uWSGI_, Gunicorn_, *or* Waitress_ (as WSGI_ server)
  * nginx_ (as `reverse proxy`_, to serve static files, for TLS_)
  * Git_ (for downloading and updating BYCEPS, but not strictly for running it)
  * uv_ (to create a virtual environment and install Python dependencies)

.. _SMTP: https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol
.. _Git: https://git-scm.com/
.. _Gunicorn: https://gunicorn.org/
.. _nginx: https://nginx.org/
.. _PostgreSQL: https://www.postgresql.org/
.. _Python: https://www.python.org/
.. _Redis: https://redis.io/
.. _reverse proxy: https://en.wikipedia.org/wiki/Reverse_proxy
.. _TLS: https://en.wikipedia.org/wiki/Transport_Layer_Security
.. _uv: https://docs.astral.sh/uv/
.. _uWSGI: https://uwsgi-docs.readthedocs.io/
.. _Waitress: https://github.com/Pylons/waitress
.. _WSGI: https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
