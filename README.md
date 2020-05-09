![tests](https://github.com/ramonmedeiros/scoreboard_bot/workflows/CI/badge.svg)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=ramonmedeiros/scoreboard_bot&identifier=245428270)](https://dependabot.com)

# Scoreboard Slack bot

Bot to log scores in office FIFA games

## Built on

1. Python & Flask
2. Postgresql
3. Heroku

## Fork and have your own. To reuse this:

1. Create a Heroku app https://devcenter.heroku.com/articles/getting-started-with-python
2. Create a postgresql on Heroku https://www.heroku.com/postgres
3. Create a App on Slack https://api.slack.com/start
4. Set the bot to write messages on the channel
5. Set SLACK_BOT_TOKEN on Heroku as environment variable with Slack Token  https://slack.com/intl/en-ee/help/articles/215770388-Create-and-regenerate-API-tokens
6. Map slash commands do endpoints /leaderboard and /report
(Guess that was)
