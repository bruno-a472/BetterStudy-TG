# Etapa 1 - Build da aplicação Angular
FROM node:20 as build

WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar dependências
RUN npm install

# Gerar build de produção
RUN npm run build -- --configuration production

# Etapa 2 - Servidor NGINX para servir os arquivos estáticos
FROM nginx:alpine

# Remover configuração default do NGINX
RUN rm -rf /usr/share/nginx/html/*

# Copiar arquivos do build Angular para a pasta padrão do NGINX
COPY --from=build /app/dist/siga-notas/browser /usr/share/nginx/html

# Copiar um arquivo customizado de configuração do NGINX (opcional)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expõe a porta
EXPOSE 80

# Comando para iniciar o NGINX
CMD ["nginx", "-g", "daemon off;"]
