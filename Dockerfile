# Use the lightweight Nginx image
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy our simple web page to the Nginx server
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80
EXPOSE 80
