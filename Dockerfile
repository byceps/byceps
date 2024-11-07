FROM python:3.11-bookworm

# Install Debian dependencies.
# A final `apt-get clean` is part of the Debian base image.
RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        locales-all \
    && \
    rm -rf /var/lib/apt/lists/*

# Don't run as root.
RUN useradd --create-home byceps
WORKDIR /home/byceps
USER byceps
ENV PATH /home/byceps/.local/bin:$PATH

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Install Python dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && \
    uv pip install --no-cache-dir uwsgi

# Install more Python dependencies, as specified by the
# application. Do this before copying the rest of the
# application's files to profit from layer caching for as long
# as the requirements specification stays the same.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements/core.txt,target=requirements.txt \
    uv pip install --no-cache-dir --requirement requirements.txt

# Copy the application into the image.
COPY . .

EXPOSE 5000
EXPOSE 8080

CMD [ \
        "uv", "run", "--no-sync", \
        "uwsgi", \
        "--callable", "app", \
        "--enable-threads", \
        "--http-socket", "0.0.0.0:8080", \
        "--lazy-apps", \
        "--processes", "8", \
        "--uwsgi-socket", "0.0.0.0:5000", \
        "--wsgi-file", "serve_apps.py" \
    ]
