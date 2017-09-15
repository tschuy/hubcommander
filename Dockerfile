FROM ubuntu:xenial

# Mostly Mike Grima: mgrima@netflix.com
MAINTAINER NetflixOSS <netflixoss@netflix.com>

# Install the Python RTM bot itself:
ARG RTM_VERSION
ADD python-rtmbot-${RTM_VERSION}.tar.gz /

RUN \
  # Install Python:
  apt-get update && \
  apt-get upgrade -y && \
  apt-get install python3 python3-venv nano -y

# Install rtmbot reqs:
RUN \
  # Rename the rtmbot:
  mv /python-rtmbot-${RTM_VERSION} /rtmbot && \

  # Set up the VENV:
  pyvenv /venv && \

  # Install all the deps:
  /bin/bash -c "source /venv/bin/activate && pip install --upgrade pip" && \
  /bin/bash -c "source /venv/bin/activate && pip install --upgrade setuptools" && \
  /bin/bash -c "source /venv/bin/activate && pip install wheel" && \
  /bin/bash -c "source /venv/bin/activate && pip install pyyaml boto3 duo_client tabulate validators rtmbot"

# Add hubcommander:
ADD / /rtmbot/hubcommander

# install hubcommander reqs and finish setup
RUN \
  # The launcher script:
  /bin/bash -c "source /venv/bin/activate && pip install /rtmbot/hubcommander" && \
  mv /rtmbot/hubcommander/launch_in_docker.sh / && chmod +x /launch_in_docker.sh && \
  rm /rtmbot/hubcommander/python-rtmbot-${RTM_VERSION}.tar.gz


# DEFINE YOUR ENV VARS FOR SECRETS HERE:
ENV SLACK_TOKEN="REPLACEMEINCMDLINE" \
    GITHUB_TOKEN="REPLACEMEINCMDLINE" \
    TRAVIS_PRO_USER="REPLACEMEINCMDLINE" \
    TRAVIS_PRO_ID="REPLACEMEINCMDLINE" \
    TRAVIS_PRO_TOKEN="REPLACEMEINCMDLINE" \
    TRAVIS_PUBLIC_USER="REPLACEMEINCMDLINE" \
    TRAVIS_PUBLIC_ID="REPLACEMEINCMDLINE" \
    TRAVIS_PUBLIC_TOKEN="REPLACEMEINCMDLINE" \
    DUO_HOST="REPLACEMEINCMDLINE" \
    DUO_IKEY="REPLACEMEINCMDLINE" \
    DUO_SKEY="REPLACEMEINCMDLINE" \
    PROMETHEUS_PORT="8080"

# Installation complete!  Ensure that things can run properly:
ENTRYPOINT ["/bin/bash", "-c", "./launch_in_docker.sh"]
