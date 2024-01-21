FROM python:3.11-bookworm

# Install Debian dependencies.
# A final `apt-get clean` is part of the Debian base image.
RUN apt-get update \
 && apt-get install --no-install-recommends --yes \
        locales-all \
 && rm -rf /var/lib/apt/lists/*

# Don't run as root.
RUN useradd --create-home byceps
WORKDIR /home/byceps
USER byceps
ENV PATH /home/byceps/.local/bin:$PATH

# Install Python dependencies.
# First, upgrade Pip itself.
RUN pip install --no-cache-dir --user --upgrade pip \
 && pip install --no-cache-dir --user uwsgi

# Install more Python dependencies, as specified by the
# application. Do this before copying the rest of the
# application's files to profit from layer caching for as long
# as the requirements specification stays the same.
COPY requirements/core.txt ./requirements.txt
RUN pip install --no-cache-dir --user --requirement requirements.txt

# Copy the application into the image.
COPY . .

# Install the `byceps` command.
RUN pip install -e .

EXPOSE 5000
EXPOSE 8080

CMD [ "uwsgi", \
      "--callable", "app", \
      "--enable-threads", \
      "--http-socket", "0.0.0.0:8080", \
      "--lazy-apps", \
      "--processes", "8", \
      "--uwsgi-socket", "0.0.0.0:5000", \
      "--wsgi-file", "serve_apps.py" \
    ]
