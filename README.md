# gmail-2-insta

This application checks for emails in a Gmail account which have a predefined subject, downloads its attachments and posts them to a predefined Instagram account.

I came up with the concept when trying to create a live social wall for my wedding. I realized that not everyone has Facebook, Instagram or Twitter, yet everyone can send an email.
The Instagram account can then be monitored by a third party live social wall service and the results shown during the event.

## Software Requirements:

- Python>=2.7

- gmail 0.0.5 by charlieguo: https://github.com/charlierguo/gmail
- InstagramAPI 1.0.2 by LevPasha: https://github.com/LevPasha/Instagram-API-python
- Pillow 5.0.0: https://github.com/python-pillow/Pillow
- moviepy 0.2.3.2 by Zulko: https://github.com/Zulko/moviepy
- schema by keleshev: https://github.com/keleshev/schema

## Non Software Requirements

The gmail account in use, must be configured to allow access by non secure applications.
More details here: https://support.google.com/accounts/answer/6010255?hl=en

## Usage:

	usage: gmail2insta.py [-h] [--conf CONF] [-v] [-d]

	Gmail to Instagram script.

	optional arguments:
	  -h, --help     show this help message and exit
	  --conf CONF    the configuration file (Default is PATH/configuration.json)
	  -v, --verbose  increase output verbosity
	  -d, --debug    increase output verbosity to debug mode
  
## Configuration File:

The configuration file must be completed by the user as it contains the username/password pairs for the gmail and instagram accounts. A template example is included in this repository. The default name is configurations.json, but it can be changed when passing the -conf argument to the script.

	{
		"gmail":

		{
			"username": "email@gmail.com",
			"password": "password",
			"attachmentsPath": "/home/na/gmail2Insta/attachments",
			"allowedSubjects":["subject"],
			"allowedImageFormats":[".jpg",".jpeg",".bmp",".gif"],
			"allowedVideoFormats":[".mp4",".avi",".mpeg"],
			"blacklist": {}
		},

		"instagram":{
			"username": "username",
			"password": "password"
		}
	}

Besides the self explanatory fields, here are the meanings of the rest:
- __attachmentsPath__ is where the downloaded attachments will be saved. Must be an existing folder.
- __allowedSubjects__ list of email subjects that will be selected for download. For now, only a single subject is allowed.
- __allowedImageFormats__ list of allowed image formats. Change this at your own risk.
- __allowedVideoFormats__ list of allowed video formats. Change this at your own risk.
- __blacklist__ dictionary of email addresses that are blacklisted (won't be downloaded)

## Behavior

Only unread emails, with the preconfigured subject and from non blacklisted email addresses will be downloaded and checked for attachments.

The application will attempt to transform images and videos into a format that Instagram accepts. The rules of Instagram for image/video sizes are taken into account before uploading as well as the creation of thumbnails for the videos.

After processing, the downloaded attachments are deleted.

## Roadmap

- Daemonization of the application.
- Encoding of the passwords to provide at least some visual protection.
- Substitution of video resizing by some video cropping algorithm that avoids deforming the contents of the video.

  
