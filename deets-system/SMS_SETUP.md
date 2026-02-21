# SMS Setup Instructions

## To Send Real SMS Messages

1. **Get Twilio Account**
   - Go to https://www.twilio.com
   - Sign up (free trial includes $15 credit)
   - Get your Account SID, Auth Token, and Phone Number

2. **Add to `.env` File**
   - Create `.env` in the `deets-system` folder
   - Add:
   ```
   ANTHROPIC_API_KEY=your_key_here
   TWILIO_ACCOUNT_SID=your_sid_here
   TWILIO_AUTH_TOKEN=your_token_here
   TWILIO_PHONE_NUMBER=+1234567890  (your Twilio number)
   ```

3. **Test SMS**
   - Create a deet in the web app
   - Use phone: `8436940053` (or your test number)
   - Click "Drop It"
   - Click "➡️ Pass" on your deet
   - Check your phone for SMS!

## How It Works

When you **pass a deet** to a friend:
1. The deet gets added to trail (visible interaction)
2. SMS is sent to their phone: `"🎯 Your deet was just passed! Score: 8.7/10"`
3. They see it immediately

## What SMS Says

```
🎯 Your deet was just passed! 
Score: [score]/10. 
Check your feed at http://localhost:5000
```

(In production, this would link to the actual app)

## Cost

- Twilio trial: $15 free credit
- Each SMS: $0.0075 (US)
- Plenty for testing!

## If Twilio Isn't Set Up

SMS sending gracefully fails (no error). The pass mechanic still works, just no notification sent.
