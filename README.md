# Alexa Skill Template w/ Custom Deploy

**Amazon's ASK CLI makes this app's custom deployment script irrelevant: https://developer.amazon.com/docs/smapi/ask-cli-command-reference.html**

A "Hello, World!" Alexa Skill.

Zip files larger than 10MB cannot be uploaded directly to AWS Lambda—they must be uploaded to S3 and then linked—so I wrote a custom deployment script to do that (`deploy.py`). However, after I had completed 80% of the script I realized that Amazon's ASK CLI handles most of this for you, so I abandoned this repo and rewrote my skill. The deployment script could still be valuable if you wanted to customize your Alexa Skills/Lambda deployment process and prefer Python/Boto. The deployment script is mostly done, but it does need to be cleaned up and tested—I wrote it in a couple hours :)
