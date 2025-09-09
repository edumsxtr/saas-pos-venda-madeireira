FROM node:18-alpine as build

WORKDIR /app

# Copiar package.json e pnpm-lock.yaml
COPY package*.json ./
COPY pnpm-lock.yaml ./

# Instalar pnpm e dependências
RUN npm install -g pnpm
RUN pnpm install

# Copiar código
COPY . .

# Build da aplicação
RUN pnpm run build

# Nginx para servir os arquivos
FROM nginx:alpine

# Copiar build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

