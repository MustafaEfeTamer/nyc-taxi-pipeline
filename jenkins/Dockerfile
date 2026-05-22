FROM jenkins/jenkins:lts

USER root

# Install prerequisites
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    python3-venv

# Add Docker's official GPG key
RUN mkdir -m 0755 -p /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker CLI and Docker Compose Plugin
RUN apt-get update && apt-get install -y docker-ce-cli docker-compose-plugin

# Ensure Jenkins user can access the docker socket
# In many host systems docker group id is 999 or similar, but since we map the socket, 
# we might need to run jenkins as root or adjust permissions dynamically.
# For simplicity in this demo, we add jenkins to root group, or we can just keep USER root for DooD.
# Running as root is easiest for local dev Docker-out-of-Docker without permission issues.
# USER jenkins

# For this demo to work smoothly with host socket mapping, we leave USER root.
# In a real production setup, you would create a docker group matching the host GID.
