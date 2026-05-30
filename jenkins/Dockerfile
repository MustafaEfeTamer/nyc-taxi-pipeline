FROM jenkins/jenkins:lts

USER root

# ─── Sistem bağımlılıkları ────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    unzip \
    wget \
    python3 \
    python3-pip \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

# ─── Docker CLI + Compose Plugin ─────────────────────────────────────────────
RUN mkdir -m 0755 -p /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null \
 && apt-get update \
 && apt-get install -y docker-ce-cli docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

# ─── SonarQube Scanner (image build sırasında kurulur, her build'de indirilmez) ─
ARG SONAR_SCANNER_VERSION=6.2.1.4610
RUN curl -sSLo /tmp/sonar-scanner.zip \
    "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux-x64.zip" \
 && unzip -q /tmp/sonar-scanner.zip -d /opt/ \
 && ln -s /opt/sonar-scanner-${SONAR_SCANNER_VERSION}-linux-x64/bin/sonar-scanner \
          /usr/local/bin/sonar-scanner \
 && rm /tmp/sonar-scanner.zip \
 && sonar-scanner --version

# ─── Jenkins kullanıcısı root grupta (DooD için) ─────────────────────────────
# Yerel geliştirme ortamı için root ile çalışıyoruz.
# Production'da docker grubunu host GID'i ile eşleştirin.
