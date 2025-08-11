FROM node:18-alpine

# 네이티브 모듈 빌드를 위한 빌드 도구 설치
RUN apk add --no-cache python3 make g++

WORKDIR /app

# 패키지 파일 복사 및 의존성 설치
COPY package*.json ./
RUN npm ci

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 애플리케이션 실행
CMD ["npm", "run", "dev"]
