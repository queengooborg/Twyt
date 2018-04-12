# Twyt
A bot to announce Twitch and YouTube uploads/livestreams.

## Prerequisites

- Python 3.5 or above
- Pip

```
python3 -m pip install discord.py
python3 -m pip install discordbot.py
python3 -m pip install opengraph
python3 -m pip install --upgrade google-api-python-client
python3 -m pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
```

## Obtaining API Keys

Note: your API keys are what associates your bot to it's own login information, along with yours.  **Do not share your API keys with anyone.**

### Discord

1. Go to the [Discord Developers](https://discordapp.com/developers/applications/me) page.
2. Click **New app** and fill out the **App Name, App Description,** and **App Icon** as desired.
3. Copy the **Client ID** at the top of the page.  This is your `client_id`.
4. Scroll down to the **Bot** section and click **Create a Bot User**, then click **Yes, do it!**
5. Click on the text that says **Click to reveal** next to **Token** and copy the revealed text.  This is your `token`.
6. While you're here, if you would like others to be able to add your bot to their servers, check the box that reads **Public Bot**.

### YouTube

1. Use [this wizard](https://console.developers.google.com/flows/enableapi?apiid=youtube) to create or select a project in the Google Developers Console and automatically turn on the API. Click **Continue**, then **Go to credentials**.
2. On the **Add credentials to your project page**, click the **Cancel** button.
3. Select the **Credentials** tab, click the **Create credentials button** and select **API key**.
4. Copy the **API key** displayed, then click **Close**.  This is your `youtube_developer_key`.

## Configuration

1. Copy `settings.sample.json` to `settings.json` and fill in the designated API key spaces.
2. Copy your Discord User ID and paste it into the `owner` slot.  Refer to the below section on how to obtain it.
3. Set the command `prefix` as desired.  Be careful about choosing a prefix that may conflict with other bots.
4. Set the description of the bot as desired.
5. Add any other cogs that you may wish to utilize in package name syntax.  Example: a cog in `cogs/myname/foo.py` will be typed as `cogs.myname.foo`.

### Obtaining your Discord User ID

1. Open the Discord application and navigate to **Settings > Appearance**.
2. Scroll down to **Advanced** and toggle the switch that reads **Developer Mode**.  If it's already enabled, then you're all set.
3. Back out of your settings and head to a chat where you've sent messages.
4. Right-click on your name and choose **Copy ID** on the context menu that appears.  Congrats, you now have your own user ID.

## FAQ

### Why does Twyt have it's name?

This is a bot designed to watch TWitch and YouTube.  Mind the capitals in those two services' names.

### But wait, so the bot's name is changing when you add more services?

Nah.  Twyt is short and simple, and changing it would just be more of a hassle than anything.  It's best to just leave it as it is, right?  :P

### Wait, why are we installing discordbot.py through Pip if you've copied all of it's files?

Because eventually, the modifications to the existing library will no longer be needed as they'll be pulled into master, plus there are possible dependencies that I would like to have imported.  I'd rather be on the safe side and have you install the package ahead of time.

## Questions

If you have any questions, feel free to reach me right here on GitHub.  You can also find me on Discord (duh) at "Vinyl Darkscratch#0640", or on my [studio's Discord server](https://discord.gg/45EQCKS).  More contact methods can be found on [my website](http://www.queengoob.org).
