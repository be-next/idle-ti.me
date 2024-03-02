# idle-ti.me website

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/be-next/idle-ti.me?logo=github)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/be-next/idle-ti.me/publish.yml?label=build%20%26%20publish)


## How to set up AWS
Recipe for serving a static website via the Amazon CloudFront distribution: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started-cloudfront-overview.html

Following this procedure, trying to obtain a missing ressource will return a 403 http error code and will diaplay a xml error message (the last produced by CloudFront). To avoid this behavior and display the ``404.html`` page instead, configure CloudFront as follows:
  - In console AWS, navigate to the CloudFront service, then select the distribution.
  - Go to the "Error Pages" tab.
  - Click on the "Create Custom Error Response" button.
  - Select the HTTP 404 and 403 errors.
  - Specify that we want to customize the error response.
  - Enter ``404.html`` in the "Response Page Path" field and set the "HTTP Response Code" to "404" for the 404 error and "403" for the 403 error.