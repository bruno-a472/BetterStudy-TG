# Etapa 1 - Build da aplicação Angular
FROM node:20 as build
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build -- --configuration production

# Etapa 2 - Servidor NGINX para servir os arquivos estáticos
FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist/siga-notas/browser /usr/share/nginx/html

# --- AQUI ESTÁ A CORREÇÃO ---
# Remove a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf
# Copia a sua configuração personalizada para o lugar dela
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta
EXPOSE 80

# Comando para iniciar o NGINX
CMD ["nginx", "-g", "daemon off;"]