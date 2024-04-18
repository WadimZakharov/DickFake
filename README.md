Dickfake Telegram bot

Build bot:

```
docker build --build-arg bot_token=your_bot_token -t dickfake-bot .
```

Run bot:

```
docker run --rm  -it -v ${pwd}/sent_images:/home/bot/sent_images dickfake-bot
```
