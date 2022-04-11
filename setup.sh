mkdir -p ~/.dashplotly/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.dashplotly/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.dashplotly/config.toml
