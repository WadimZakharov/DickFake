Dickfake Telegram bot

Build bot:

```
docker build --build-arg -t dickfake-bot .
```

Run bot:

```
docker run --rm  -it -v ${pwd}/sent_images:/home/bot/sent_images bot_token=your_bot_token dickfake-bot
```
